# Cross-Ability Plugin System

A pluggable provider framework that enables ESP32 devices to connect to
**MCP servers** and **VNC endpoints** from mobile devices, giving you
remote control of base servers and computers.

## Overview

| Provider | Purpose | Default |
|----------|---------|---------|
| **MCP** | Connect to Model Context Protocol servers and route tool calls | Disabled |
| **VNC** | Initiate remote desktop sessions to base servers/computers | Disabled |

Both providers are **disabled by default**. Enable them at compile time or
at runtime through the plugin manager.

## Quick Start

```c
#include "plugins/cross_ability/cross_ability.h"
#include "plugins/cross_ability/mcp_provider.h"
#include "plugins/cross_ability/vnc_provider.h"

void app_main(void) {
    /* Initialize the plugin manager */
    cross_ability_manager_init();

    /* Create and register providers */
    cross_ability_provider_t *mcp = mcp_provider_create();
    mcp->enabled = true;                /* enable at runtime */
    cross_ability_register(mcp);

    cross_ability_provider_t *vnc = vnc_provider_create();
    vnc->enabled = true;
    cross_ability_register(vnc);

    /* Connect the MCP provider from a mobile device */
    cross_ability_conn_params_t params = {
        .host        = "192.168.1.100",
        .port        = 3000,
        .auth_token  = NULL,
        .timeout_ms  = 10000,
        .from_mobile = true
    };
    mcp->connect(mcp, &params);

    /* Route a tool call */
    mcp_tool_call_t call = {
        .tool_name      = "list_files",
        .arguments_json = "{\"path\": \"/\"}"
    };
    mcp_provider_tool_call(mcp, &call);

    /* Connect VNC to a base computer */
    params.host = "192.168.1.200";
    params.port = 5900;
    vnc->connect(vnc, &params);

    /* Clean up */
    cross_ability_manager_shutdown();
}
```

## Compile-Time Configuration

Override any of these in your build flags (e.g. `-DCROSS_ABILITY_ENABLE_MCP=1`):

| Define | Default | Description |
|--------|---------|-------------|
| `CROSS_ABILITY_ENABLE_MCP` | `0` | Enable MCP provider |
| `CROSS_ABILITY_ENABLE_VNC` | `0` | Enable VNC provider |
| `CROSS_ABILITY_MAX_PROVIDERS` | `8` | Max registered providers |
| `CROSS_ABILITY_MCP_DEFAULT_PORT` | `3000` | Default MCP server port |
| `CROSS_ABILITY_VNC_DEFAULT_PORT` | `5900` | Default VNC server port |
| `CROSS_ABILITY_CONNECT_TIMEOUT_MS` | `10000` | Connection timeout (ms) |
| `CROSS_ABILITY_ALLOW_MOBILE` | `1` | Allow mobile device connections |

## Architecture

```
┌──────────────────────────────────────┐
│         Mobile Device                │
│  (triggers tool calls / VNC input)   │
└──────────────┬───────────────────────┘
               │
     ┌─────────▼─────────┐
     │   Plugin Manager   │
     │  (cross_ability.c) │
     └──┬────────────┬────┘
        │            │
  ┌─────▼──┐   ┌────▼───┐
  │  MCP   │   │  VNC   │
  │Provider│   │Provider│
  └───┬────┘   └───┬────┘
      │            │
  ┌───▼────┐  ┌───▼──────┐
  │MCP     │  │VNC       │
  │Server  │  │Server /  │
  │        │  │Computer  │
  └────────┘  └──────────┘
```

## License

Apache License 2.0 — see [LICENSE](../../LICENSE).
