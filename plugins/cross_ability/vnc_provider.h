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

#ifndef VNC_PROVIDER_H
#define VNC_PROVIDER_H

#include "cross_ability.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * VNC provider context (opaque to callers).
 */
typedef struct {
    char host[128];
    uint16_t port;
    bool connected;
} vnc_provider_ctx_t;

/**
 * Create and return a cross-ability provider backed by VNC.
 *
 * The returned provider is disabled by default; enable it by setting
 * provider->enabled = true (or compile with CROSS_ABILITY_ENABLE_VNC=1).
 */
cross_ability_provider_t *vnc_provider_create(void);

#ifdef __cplusplus
}
#endif

#endif /* VNC_PROVIDER_H */
