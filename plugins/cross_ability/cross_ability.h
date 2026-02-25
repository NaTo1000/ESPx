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

#ifndef CROSS_ABILITY_H
#define CROSS_ABILITY_H

#include "config.h"
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Provider type identifiers.
 */
typedef enum {
    PROVIDER_TYPE_MCP = 0,
    PROVIDER_TYPE_VNC = 1
} cross_ability_provider_type_t;

/**
 * Connection status codes.
 */
typedef enum {
    CROSS_ABILITY_OK = 0,
    CROSS_ABILITY_ERR_DISABLED = -1,
    CROSS_ABILITY_ERR_CONNECT = -2,
    CROSS_ABILITY_ERR_TIMEOUT = -3,
    CROSS_ABILITY_ERR_AUTH = -4,
    CROSS_ABILITY_ERR_NO_PROVIDER = -5,
    CROSS_ABILITY_ERR_FULL = -6,
    CROSS_ABILITY_ERR_PERMISSION = -7
} cross_ability_err_t;

/**
 * Connection parameters shared by all providers.
 */
typedef struct {
    const char *host;
    uint16_t port;
    const char *auth_token;
    uint32_t timeout_ms;
    bool from_mobile;
} cross_ability_conn_params_t;

/**
 * Abstract provider interface.
 *
 * Each provider implements these callbacks to handle connections,
 * data exchange, and cleanup.
 */
typedef struct cross_ability_provider {
    const char *name;
    cross_ability_provider_type_t type;
    bool enabled;

    cross_ability_err_t (*init)(struct cross_ability_provider *self);
    cross_ability_err_t (*connect)(struct cross_ability_provider *self,
                                  const cross_ability_conn_params_t *params);
    cross_ability_err_t (*send)(struct cross_ability_provider *self,
                                const uint8_t *data, uint32_t len);
    cross_ability_err_t (*disconnect)(struct cross_ability_provider *self);
    void (*destroy)(struct cross_ability_provider *self);

    void *ctx; /* provider-specific context */
} cross_ability_provider_t;

/**
 * Initialize the cross-ability plugin manager.
 */
cross_ability_err_t cross_ability_manager_init(void);

/**
 * Register a provider with the plugin manager.
 *
 * @param provider  Pointer to an initialized provider struct.
 * @return CROSS_ABILITY_OK on success, error code otherwise.
 */
cross_ability_err_t cross_ability_register(cross_ability_provider_t *provider);

/**
 * Look up a registered provider by type.
 *
 * @param type  The provider type to find.
 * @return Pointer to the provider, or NULL if not found.
 */
cross_ability_provider_t *cross_ability_get_provider(
    cross_ability_provider_type_t type);

/**
 * Return the number of currently registered providers.
 */
int cross_ability_provider_count(void);

/**
 * Tear down the plugin manager and destroy all providers.
 */
void cross_ability_manager_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* CROSS_ABILITY_H */
