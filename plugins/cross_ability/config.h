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

#ifndef CROSS_ABILITY_CONFIG_H
#define CROSS_ABILITY_CONFIG_H

/*
 * Cross-Ability Plugin Configuration
 *
 * All providers are disabled by default. Enable them explicitly
 * in your build configuration or at runtime via the plugin manager.
 */

/* Set to 1 to enable the MCP server provider at compile time */
#ifndef CROSS_ABILITY_ENABLE_MCP
#define CROSS_ABILITY_ENABLE_MCP 0
#endif

/* Set to 1 to enable the VNC provider at compile time */
#ifndef CROSS_ABILITY_ENABLE_VNC
#define CROSS_ABILITY_ENABLE_VNC 0
#endif

/* Maximum number of registered providers */
#ifndef CROSS_ABILITY_MAX_PROVIDERS
#define CROSS_ABILITY_MAX_PROVIDERS 8
#endif

/* Default MCP server port */
#ifndef CROSS_ABILITY_MCP_DEFAULT_PORT
#define CROSS_ABILITY_MCP_DEFAULT_PORT 3000
#endif

/* Default VNC server port */
#ifndef CROSS_ABILITY_VNC_DEFAULT_PORT
#define CROSS_ABILITY_VNC_DEFAULT_PORT 5900
#endif

/* Connection timeout in milliseconds */
#ifndef CROSS_ABILITY_CONNECT_TIMEOUT_MS
#define CROSS_ABILITY_CONNECT_TIMEOUT_MS 10000
#endif

/* Permission: allow mobile device connections */
#ifndef CROSS_ABILITY_ALLOW_MOBILE
#define CROSS_ABILITY_ALLOW_MOBILE 1
#endif

#endif /* CROSS_ABILITY_CONFIG_H */
