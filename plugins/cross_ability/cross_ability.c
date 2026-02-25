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

#include "cross_ability.h"
#include <stddef.h>
#include <string.h>

static cross_ability_provider_t *providers[CROSS_ABILITY_MAX_PROVIDERS];
static int provider_count = 0;
static bool manager_initialized = false;

cross_ability_err_t cross_ability_manager_init(void) {
    memset(providers, 0, sizeof(providers));
    provider_count = 0;
    manager_initialized = true;
    return CROSS_ABILITY_OK;
}

cross_ability_err_t cross_ability_register(cross_ability_provider_t *provider) {
    if (!manager_initialized) {
        return CROSS_ABILITY_ERR_DISABLED;
    }
    if (provider == NULL) {
        return CROSS_ABILITY_ERR_NO_PROVIDER;
    }
    if (provider_count >= CROSS_ABILITY_MAX_PROVIDERS) {
        return CROSS_ABILITY_ERR_FULL;
    }
    providers[provider_count++] = provider;
    return CROSS_ABILITY_OK;
}

cross_ability_provider_t *cross_ability_get_provider(
    cross_ability_provider_type_t type) {
    for (int i = 0; i < provider_count; i++) {
        if (providers[i] != NULL && providers[i]->type == type) {
            return providers[i];
        }
    }
    return NULL;
}

int cross_ability_provider_count(void) {
    return provider_count;
}

void cross_ability_manager_shutdown(void) {
    for (int i = 0; i < provider_count; i++) {
        if (providers[i] != NULL && providers[i]->destroy != NULL) {
            providers[i]->destroy(providers[i]);
        }
        providers[i] = NULL;
    }
    provider_count = 0;
    manager_initialized = false;
}
