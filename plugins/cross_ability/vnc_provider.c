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

#include "vnc_provider.h"
#include <stdlib.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* Provider callbacks                                                  */
/* ------------------------------------------------------------------ */

static cross_ability_err_t vnc_init(cross_ability_provider_t *self) {
    if (self == NULL || self->ctx == NULL) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    vnc_provider_ctx_t *ctx = (vnc_provider_ctx_t *)self->ctx;
    memset(ctx->host, 0, sizeof(ctx->host));
    ctx->port = CROSS_ABILITY_VNC_DEFAULT_PORT;
    ctx->connected = false;
    return CROSS_ABILITY_OK;
}

static cross_ability_err_t vnc_connect(cross_ability_provider_t *self,
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

    vnc_provider_ctx_t *ctx = (vnc_provider_ctx_t *)self->ctx;
    if (params->host != NULL) {
        strncpy(ctx->host, params->host, sizeof(ctx->host) - 1);
    }
    ctx->port = params->port ? params->port : CROSS_ABILITY_VNC_DEFAULT_PORT;

    /*
     * TODO: Perform the real VNC handshake (RFB protocol) with the
     * remote server.  For now we mark the session as connected.
     */
    ctx->connected = true;
    return CROSS_ABILITY_OK;
}

static cross_ability_err_t vnc_send(cross_ability_provider_t *self,
                                    const uint8_t *data, uint32_t len) {
    if (self == NULL || data == NULL || len == 0) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    vnc_provider_ctx_t *ctx = (vnc_provider_ctx_t *)self->ctx;
    if (!ctx->connected) {
        return CROSS_ABILITY_ERR_CONNECT;
    }
    /*
     * TODO: Forward framebuffer update requests or key/pointer
     * events to the VNC server.
     */
    return CROSS_ABILITY_OK;
}

static cross_ability_err_t vnc_disconnect(cross_ability_provider_t *self) {
    if (self == NULL) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    vnc_provider_ctx_t *ctx = (vnc_provider_ctx_t *)self->ctx;
    ctx->connected = false;
    return CROSS_ABILITY_OK;
}

static void vnc_destroy(cross_ability_provider_t *self) {
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

cross_ability_provider_t *vnc_provider_create(void) {
    cross_ability_provider_t *p = calloc(1, sizeof(*p));
    if (p == NULL) {
        return NULL;
    }
    vnc_provider_ctx_t *ctx = calloc(1, sizeof(*ctx));
    if (ctx == NULL) {
        free(p);
        return NULL;
    }

    p->name = "vnc";
    p->type = PROVIDER_TYPE_VNC;
    p->enabled = (CROSS_ABILITY_ENABLE_VNC != 0);
    p->init = vnc_init;
    p->connect = vnc_connect;
    p->send = vnc_send;
    p->disconnect = vnc_disconnect;
    p->destroy = vnc_destroy;
    p->ctx = ctx;

    return p;
}
