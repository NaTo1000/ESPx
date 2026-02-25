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

#include "mcp_provider.h"
#include <stdlib.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* Provider callbacks                                                  */
/* ------------------------------------------------------------------ */

static cross_ability_err_t mcp_init(cross_ability_provider_t *self) {
    if (self == NULL || self->ctx == NULL) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    mcp_provider_ctx_t *ctx = (mcp_provider_ctx_t *)self->ctx;
    memset(ctx->host, 0, sizeof(ctx->host));
    ctx->port = CROSS_ABILITY_MCP_DEFAULT_PORT;
    ctx->connected = false;
    return CROSS_ABILITY_OK;
}

static cross_ability_err_t mcp_connect(cross_ability_provider_t *self,
                                       const cross_ability_conn_params_t *params) {
    if (self == NULL || params == NULL) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    if (!self->enabled) {
        return CROSS_ABILITY_ERR_DISABLED;
    }
    if (params->from_mobile && !CROSS_ABILITY_ALLOW_MOBILE) {
        return CROSS_ABILITY_ERR_PERMISSION;
    }

    mcp_provider_ctx_t *ctx = (mcp_provider_ctx_t *)self->ctx;
    if (params->host != NULL) {
        strncpy(ctx->host, params->host, sizeof(ctx->host) - 1);
    }
    ctx->port = params->port ? params->port : CROSS_ABILITY_MCP_DEFAULT_PORT;

    /*
     * TODO: Open a real TCP/TLS connection to the MCP server.
     * For now we mark the provider as connected so higher layers
     * can exercise the full call path.
     */
    ctx->connected = true;
    return CROSS_ABILITY_OK;
}

static cross_ability_err_t mcp_send(cross_ability_provider_t *self,
                                    const uint8_t *data, uint32_t len) {
    if (self == NULL || data == NULL || len == 0) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    mcp_provider_ctx_t *ctx = (mcp_provider_ctx_t *)self->ctx;
    if (!ctx->connected) {
        return CROSS_ABILITY_ERR_CONNECT;
    }
    /*
     * TODO: Forward the raw payload to the MCP server over the
     * established connection.
     */
    return CROSS_ABILITY_OK;
}

static cross_ability_err_t mcp_disconnect(cross_ability_provider_t *self) {
    if (self == NULL) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    mcp_provider_ctx_t *ctx = (mcp_provider_ctx_t *)self->ctx;
    ctx->connected = false;
    return CROSS_ABILITY_OK;
}

static void mcp_destroy(cross_ability_provider_t *self) {
    if (self == NULL) {
        return;
    }
    free(self->ctx);
    self->ctx = NULL;
    free(self);
}

/* ------------------------------------------------------------------ */
/* Public API                                                          */
/* ------------------------------------------------------------------ */

cross_ability_provider_t *mcp_provider_create(void) {
    cross_ability_provider_t *p = calloc(1, sizeof(*p));
    if (p == NULL) {
        return NULL;
    }
    mcp_provider_ctx_t *ctx = calloc(1, sizeof(*ctx));
    if (ctx == NULL) {
        free(p);
        return NULL;
    }

    p->name = "mcp";
    p->type = PROVIDER_TYPE_MCP;
    p->enabled = (CROSS_ABILITY_ENABLE_MCP != 0);
    p->init = mcp_init;
    p->connect = mcp_connect;
    p->send = mcp_send;
    p->disconnect = mcp_disconnect;
    p->destroy = mcp_destroy;
    p->ctx = ctx;

    return p;
}

cross_ability_err_t mcp_provider_tool_call(cross_ability_provider_t *provider,
                                           const mcp_tool_call_t *call) {
    if (provider == NULL || call == NULL) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    if (!provider->enabled) {
        return CROSS_ABILITY_ERR_DISABLED;
    }
    /*
     * Serialize the tool call as JSON and send it through the
     * generic send path.  A real implementation would build a
     * proper MCP JSON-RPC request here.
     */
    const char *json = call->arguments_json ? call->arguments_json : "{}";
    return provider->send(provider, (const uint8_t *)json,
                          (uint32_t)strlen(json));
}
