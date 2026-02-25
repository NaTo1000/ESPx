# ESPx
Full ESP32 wireless suite — come have a look, add to it, make it next level 😄

## Splash screen

A Wild-West-themed startup GUI lives in `splash/index.html`.  Open it in any
browser to see:

* **Flipper Zero-inspired dolphin** wrangling four ESP32 modules with animated lasso ropes
* **3-D rotating torus-knot** (Three.js) rendered in liquid gold as an infinity / AI-loop symbol
* **"iNFINITEAi2025"** title with animated gold-shine calligraphy
* Parallax star field, desert mesa silhouettes, cactus, and tumbleweed
* Animated SVG **∞** infinity symbol with a shimmering stroke
* Simulated loading bar cycling through startup phases
* Fully responsive — works on mobile, desktop, and server-side headless browsers

```bash
# Open locally
open splash/index.html          # macOS
xdg-open splash/index.html      # Linux
start splash/index.html         # Windows
```

## Content-upgrade pipeline

The `pipeline/` package is a parallel research-bot system that fetches,
caches, and displays feeds for ESP32 firmware, security CVEs, AI models, and
robotics libraries.

### Quick start

```bash
pip install -r requirements.txt

# list all registered feeds
python -m pipeline --list-feeds

# run all feeds (results cached for 1 h)
python -m pipeline

# filter by tag
python -m pipeline --tag esp32
python -m pipeline --tag ai
python -m pipeline --tag security

# skip cache
python -m pipeline --no-cache

# custom TTL (seconds)
python -m pipeline --ttl 300
```

### Architecture

| Component | File | Role |
|-----------|------|------|
| Feed registry | `pipeline/feed.py` | Declares remote sources (GitHub releases, NVD CVEs, Hugging Face, ROS 2) |
| Research agents | `pipeline/agent.py` | HTTP fetch + kind-specific parsers; parallel via `ThreadPoolExecutor` |
| Cache | `pipeline/cache.py` | JSON-file cache under `~/.cache/espx/` simulating fast NVMe-backed storage |
| CLI entry-point | `pipeline/main.py` | Rich terminal UI; `--tag`, `--no-cache`, `--ttl`, `--list-feeds` |

### Tests

```bash
python -m pytest tests/ -v
```
