/*
 * Copyright 2026 ESPx Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MCP_PROVIDER_H
#define MCP_PROVIDER_H

#include "cross_ability.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * MCP tool-call request forwarded from a mobile device.
 */
typedef struct {
    const char *tool_name;
    const char *arguments_json;
} mcp_tool_call_t;

/**
 * MCP provider context (opaque to callers).
 */
typedef struct {
    char host[128];
    uint16_t port;
    bool connected;
} mcp_provider_ctx_t;

/**
 * Create and return a cross-ability provider backed by MCP.
 *
 * The returned provider is disabled by default; enable it by setting
 * provider->enabled = true (or compile with CROSS_ABILITY_ENABLE_MCP=1).
 */
cross_ability_provider_t *mcp_provider_create(void);

/**
 * Send a tool call through the MCP provider.
 *
 * @param provider  MCP provider instance.
 * @param call      Tool call to route to the MCP server.
 * @return CROSS_ABILITY_OK on success, error code otherwise.
 */
cross_ability_err_t mcp_provider_tool_call(cross_ability_provider_t *provider,
                                           const mcp_tool_call_t *call);

#ifdef __cplusplus
}
#endif

#endif /* MCP_PROVIDER_H */
