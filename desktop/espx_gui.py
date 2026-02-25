#!/usr/bin/env python3
"""
ESPx Desktop GUI
================
Connects to an ESPx-flashed ESP32 over a serial port and provides:
  - Live WiFi network scanning (SSID, BSSID, RSSI, channel, band, encryption)
  - Live BLE device scanning (name, address, RSSI, manufacturer data)
  - Persistent SQLite logging via scanner_db
  - Scan history and aggregated statistics
  - CSV export

Usage::

    pip install pyserial
    python espx_gui.py
"""

import csv
import json
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import serial
import serial.tools.list_ports

import scanner_db

# ──────────────────────────────────────────────────────────────────────────────
APP_TITLE   = "ESPx Wireless Scanner"
APP_VERSION = "1.0.0"
BAUD_RATE   = 115200

WIFI_COLUMNS = ("ssid", "bssid", "rssi", "channel", "band", "encryption")
BLE_COLUMNS  = ("name", "address", "rssi", "manufacturer_data", "service_uuid")
# ──────────────────────────────────────────────────────────────────────────────


class ESPxApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_TITLE}  v{APP_VERSION}")
        self.geometry("1150x700")
        self.minsize(800, 500)

        scanner_db.init_db()

        self._serial: serial.Serial | None = None
        self._rx_queue: queue.Queue = queue.Queue()
        self._rx_thread: threading.Thread | None = None

        self._build_menu()
        self._build_toolbar()
        self._build_notebook()
        self._build_statusbar()

        self._refresh_ports()
        self.after(200, self._poll_rx_queue)

    # ── Menu ──────────────────────────────────────────────────────────────────
    def _build_menu(self) -> None:
        menu = tk.Menu(self)
        self.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export WiFi CSV…", command=self._export_wifi_csv)
        file_menu.add_command(label="Export BLE CSV…",  command=self._export_ble_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        help_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self, relief="raised")
        bar.pack(side="top", fill="x")

        ttk.Label(bar, text="Port:").pack(side="left", padx=(8, 2), pady=4)
        self._port_var = tk.StringVar()
        self._port_cb = ttk.Combobox(
            bar, textvariable=self._port_var, width=18, state="readonly"
        )
        self._port_cb.pack(side="left", padx=2, pady=4)
        ttk.Button(bar, text="⟳", width=3,
                   command=self._refresh_ports).pack(side="left", padx=2, pady=4)

        self._connect_btn = ttk.Button(bar, text="Connect",
                                       command=self._toggle_connect)
        self._connect_btn.pack(side="left", padx=8, pady=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=6)

        self._scan_wifi_btn = ttk.Button(
            bar, text="📡 Scan WiFi", command=self._cmd_scan_wifi, state="disabled"
        )
        self._scan_wifi_btn.pack(side="left", padx=4, pady=4)

        self._scan_ble_btn = ttk.Button(
            bar, text="🔵 Scan BLE", command=self._cmd_scan_ble, state="disabled"
        )
        self._scan_ble_btn.pack(side="left", padx=4, pady=4)

        ttk.Label(bar, text="BLE secs:").pack(side="left", padx=(8, 2))
        self._ble_secs = tk.IntVar(value=5)
        ttk.Spinbox(bar, from_=1, to=30,
                    textvariable=self._ble_secs, width=4).pack(side="left", padx=2)

    # ── Notebook ──────────────────────────────────────────────────────────────
    def _build_notebook(self) -> None:
        self._nb = ttk.Notebook(self)
        self._nb.pack(expand=True, fill="both", padx=4, pady=4)

        wifi_frame, self._wifi_tree = self._make_tree_tab(WIFI_COLUMNS)
        ble_frame,  self._ble_tree  = self._make_tree_tab(BLE_COLUMNS)
        log_frame                   = self._make_log_tab()
        hist_frame                  = self._make_history_tab()

        self._nb.add(wifi_frame, text="📡  WiFi")
        self._nb.add(ble_frame,  text="🔵  BLE")
        self._nb.add(log_frame,  text="📋  Log")
        self._nb.add(hist_frame, text="🗄  History")

    def _make_tree_tab(self, columns: tuple) -> tuple:
        frame = ttk.Frame(self._nb)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        tree = ttk.Treeview(frame, columns=columns,
                             show="headings", selectmode="browse")
        for col in columns:
            tree.heading(
                col,
                text=col.replace("_", " ").title(),
                command=lambda c=col, t=tree: self._sort_tree(t, c, False),
            )
            tree.column(col, width=140, anchor="w")
        tree.column("rssi", width=60, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        return frame, tree

    def _make_log_tab(self) -> ttk.Frame:
        frame = ttk.Frame(self._nb)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self._log_text = tk.Text(
            frame, wrap="none", font=("Courier", 10),
            background="#1e1e1e", foreground="#d4d4d4",
            insertbackground="white",
        )
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=vsb.set)
        self._log_text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        ttk.Button(
            frame, text="Clear Log",
            command=lambda: self._log_text.delete("1.0", "end"),
        ).grid(row=1, column=0, sticky="w", padx=4, pady=2)
        return frame

    def _make_history_tab(self) -> ttk.Frame:
        frame = ttk.Frame(self._nb)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="🔄 Refresh History",
                   command=self._load_history).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=4, pady=4
        )

        # WiFi history
        wf = ttk.LabelFrame(frame, text="Unique WiFi Networks (all-time)")
        wf.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        wf.rowconfigure(0, weight=1)
        wf.columnconfigure(0, weight=1)
        wcols = ("ssid", "bssid", "best_rssi", "seen_count", "last_seen", "band")
        self._hist_wifi = ttk.Treeview(wf, columns=wcols, show="headings")
        for c in wcols:
            self._hist_wifi.heading(c, text=c.replace("_", " ").title())
            self._hist_wifi.column(c, width=110)
        vsb = ttk.Scrollbar(wf, orient="vertical", command=self._hist_wifi.yview)
        self._hist_wifi.configure(yscrollcommand=vsb.set)
        self._hist_wifi.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # BLE history
        bf = ttk.LabelFrame(frame, text="Unique BLE Devices (all-time)")
        bf.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        bf.rowconfigure(0, weight=1)
        bf.columnconfigure(0, weight=1)
        bcols = ("name", "address", "best_rssi", "seen_count", "last_seen")
        self._hist_ble = ttk.Treeview(bf, columns=bcols, show="headings")
        for c in bcols:
            self._hist_ble.heading(c, text=c.replace("_", " ").title())
            self._hist_ble.column(c, width=120)
        vsb2 = ttk.Scrollbar(bf, orient="vertical", command=self._hist_ble.yview)
        self._hist_ble.configure(yscrollcommand=vsb2.set)
        self._hist_ble.grid(row=0, column=0, sticky="nsew")
        vsb2.grid(row=0, column=1, sticky="ns")

        return frame

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_statusbar(self) -> None:
        bar = ttk.Frame(self, relief="sunken")
        bar.pack(side="bottom", fill="x")
        self._status_var = tk.StringVar(value="Disconnected")
        ttk.Label(bar, textvariable=self._status_var, anchor="w").pack(
            side="left", padx=8
        )

    # ── Serial helpers ────────────────────────────────────────────────────────
    def _refresh_ports(self) -> None:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self._port_cb["values"] = ports
        if ports and not self._port_var.get():
            self._port_var.set(ports[0])

    def _toggle_connect(self) -> None:
        if self._serial and self._serial.is_open:
            self._disconnect()
        else:
            self._connect()

    def _connect(self) -> None:
        port = self._port_var.get()
        if not port:
            messagebox.showerror("No port", "Please select a serial port.")
            return
        try:
            self._serial = serial.Serial(port, BAUD_RATE, timeout=1)
            self._rx_thread = threading.Thread(
                target=self._rx_worker, daemon=True
            )
            self._rx_thread.start()
            self._connect_btn.config(text="Disconnect")
            self._scan_wifi_btn.config(state="normal")
            self._scan_ble_btn.config(state="normal")
            self._set_status(f"Connected  {port}  @  {BAUD_RATE} baud")
            self._log(f"[INFO] Connected to {port}")
        except serial.SerialException as exc:
            messagebox.showerror("Connection error", str(exc))

    def _disconnect(self) -> None:
        if self._serial:
            self._serial.close()
            self._serial = None
        self._connect_btn.config(text="Connect")
        self._scan_wifi_btn.config(state="disabled")
        self._scan_ble_btn.config(state="disabled")
        self._set_status("Disconnected")
        self._log("[INFO] Disconnected")

    def _send_command(self, cmd: str) -> None:
        if self._serial and self._serial.is_open:
            self._serial.write((cmd + "\n").encode())
            self._log(f"[CMD]  {cmd}")

    def _cmd_scan_wifi(self) -> None:
        self._send_command("SCAN_WIFI")
        self._nb.select(0)

    def _cmd_scan_ble(self) -> None:
        self._send_command(f"SCAN_BLE {self._ble_secs.get()}")
        self._nb.select(1)

    # ── RX thread & queue ────────────────────────────────────────────────────
    def _rx_worker(self) -> None:
        while self._serial and self._serial.is_open:
            try:
                line = self._serial.readline().decode("utf-8", errors="replace").strip()
                if line:
                    self._rx_queue.put(line)
            except Exception:
                break

    def _poll_rx_queue(self) -> None:
        while not self._rx_queue.empty():
            self._process_rx_line(self._rx_queue.get_nowait())
        self.after(100, self._poll_rx_queue)

    def _process_rx_line(self, line: str) -> None:
        self._log(f"[RX]   {line}")
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return

        msg_type = data.get("type", "")

        if msg_type == "wifi_scan":
            networks = data.get("networks", [])
            self._populate_tree(self._wifi_tree, networks, WIFI_COLUMNS)
            scanner_db.store_wifi_scan(networks)
            self._set_status(f"WiFi scan complete — {len(networks)} networks")

        elif msg_type == "ble_scan":
            devices = data.get("devices", [])
            self._populate_tree(self._ble_tree, devices, BLE_COLUMNS)
            scanner_db.store_ble_scan(devices)
            self._set_status(f"BLE scan complete — {len(devices)} devices")

        elif msg_type == "status":
            self._set_status(data.get("message", str(data)))

    # ── Tree helpers ──────────────────────────────────────────────────────────
    def _populate_tree(self, tree: ttk.Treeview, rows: list, columns: tuple) -> None:
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=[row.get(c, "") for c in columns])

    def _sort_tree(self, tree: ttk.Treeview, col: str, reverse: bool) -> None:
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] != "" else 0,
                      reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for i, (_, k) in enumerate(data):
            tree.move(k, "", i)
        tree.heading(col,
                     command=lambda: self._sort_tree(tree, col, not reverse))

    # ── History ───────────────────────────────────────────────────────────────
    def _load_history(self) -> None:
        data = scanner_db.get_unique_networks()

        for item in self._hist_wifi.get_children():
            self._hist_wifi.delete(item)
        for r in data["wifi"]:
            self._hist_wifi.insert("", "end", values=(
                r.get("ssid", ""), r.get("bssid", ""),
                r.get("best_rssi", ""), r.get("seen_count", ""),
                (r.get("last_seen") or "")[:19], r.get("band", ""),
            ))

        for item in self._hist_ble.get_children():
            self._hist_ble.delete(item)
        for r in data["ble"]:
            self._hist_ble.insert("", "end", values=(
                r.get("name", ""), r.get("address", ""),
                r.get("best_rssi", ""), r.get("seen_count", ""),
                (r.get("last_seen") or "")[:19],
            ))

    # ── Export ────────────────────────────────────────────────────────────────
    def _export_wifi_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export WiFi History",
        )
        if not path:
            return
        rows = scanner_db.get_wifi_history()
        if not rows:
            messagebox.showinfo("Export", "No WiFi data to export.")
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        self._log(f"[INFO] Exported WiFi history → {path}")

    def _export_ble_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export BLE History",
        )
        if not path:
            return
        rows = scanner_db.get_ble_history()
        if not rows:
            messagebox.showinfo("Export", "No BLE data to export.")
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        self._log(f"[INFO] Exported BLE history → {path}")

    # ── Misc ──────────────────────────────────────────────────────────────────
    def _set_status(self, msg: str) -> None:
        self._status_var.set(msg)

    def _log(self, msg: str) -> None:
        self._log_text.insert("end", msg + "\n")
        self._log_text.see("end")

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About ESPx",
            f"{APP_TITLE}  v{APP_VERSION}\n\n"
            "Comprehensive ESP32 WiFi & BLE scanning suite.\n"
            "Compatible with ESP32, LilyGo T-Display, ESP32-S3 and more.\n\n"
            "Scan results are persisted in  ~/.espx/scans.db\n\n"
            "github.com/NaTo1000/ESPx",
        )


def main() -> None:
    app = ESPxApp()
    app.mainloop()


if __name__ == "__main__":
    main()
