# ESPx

Full ESP32/ESP8266 wireless suite — come have a look, add to it, make it next level 😉

## ESPiritAi — Central Orchestration Engine

ESPiritAi is the advanced AI orchestration model at the heart of ESPx.  It acts
as the central 'brains' for all operations, integrating:

| Subsystem | Description |
|---|---|
| **Knowledge Base** | Comprehensive data on ESP32/ESP8266 variants, firmware types, programming languages, operational values, weaknesses, and related projects (Marauder, Meshtastic, RoboticsDashboard, …) |
| **Self-Upgrading Algorithms** | Reinforcement learning (Q-learning + replay buffer) and meta-learning (MAML-inspired) for continuous autonomous improvement |
| **Simulation Runners** | Virtual ESP hardware emulator and risk assessor for safe testing without physical devices |
| **Multi-AI Council** | Ensemble of specialised advisors (Security, Performance, Network) with weighted-consensus decision engine |
| **CHAIMERA** | Custom Hybrid AI fRAMEwoRk — blends symbolic reasoning, fuzzy logic, Bayesian classification, evolutionary algorithms, and neural networks into a single inference engine |
| **Three-Speed Engines** | Fast (real-time control, <1 ms), Medium (analysis, sub-second), Slow (deep learning / batch) engine tiers |
| **Cloud Compute** | Distributed processing client + Hugging Face model integration (code-gen, QA, classification, embeddings) |
| **Background Modes** | Periodic task scheduler for P2P orchestration, research pipelines, and system health checks |
| **API Vault** | HMAC-hardened in-memory secret store with audit logging and lock/unlock controls |
| **P2P Network** | Secure key-sharing and message routing across ESPx nodes |

### Quick Start

```python
from espx import ESPiritAi

ai = ESPiritAi()

# Make an orchestration decision
decision = ai.decide({
    "risk_score": 0.2,
    "cpu_usage_pct": 35.0,
    "heap_free_b": 160_000,
    "wifi_connected": True,
})
print(decision["final_action"])  # e.g. "optimize_scan"

# Query the knowledge base
chip = ai.knowledge.get_chip("ESP32")
print(chip.weaknesses)

# Run a virtual simulation
result = ai.simulate("wifi_audit")
print(result.risk_report.level)   # RiskLevel.LOW / MEDIUM / HIGH / CRITICAL

# Store an API key securely
ai.store_api_key("hf_token", "hf-xxxx", service="huggingface")

# Get system status
print(ai.status())
```

### Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

### Package Structure

```
espx/
├── espiritai/
│   ├── core.py          # ESPiritAi — main orchestrator
│   ├── knowledge.py     # Chip / firmware / project knowledge base
│   ├── algorithms.py    # RL + meta-learning self-upgrader
│   ├── simulation.py    # Virtual ESP emulator + risk assessor
│   ├── council.py       # Multi-AI council + consensus engine
│   ├── chaimera.py      # CHAIMERA hybrid AI framework
│   ├── engines.py       # Three-speed AI engine tiers
│   ├── cloud.py         # Cloud compute + Hugging Face client
│   └── background.py    # Background modes (P2P, pipelines, scheduler)
├── vault/
│   └── vault.py         # Secure API vault
└── p2p/
    └── network.py       # P2P key-sharing and messaging
tests/
└── test_espiritai.py
```

### Supported Chips

ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-H2, ESP8266, ESP-01

### Supported Firmware

Arduino, ESP-IDF, MicroPython, Tasmota, ESPHome, Marauder, Meshtastic, NodeMCU
