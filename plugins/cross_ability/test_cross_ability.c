/*
 * Cross-Ability Plugin — unit tests
 *
 * Compile:
 *   cc -I../.. -o test_cross_ability test_cross_ability.c \
 *      cross_ability.c mcp_provider.c vnc_provider.c
 *
 * Run:
 *   ./test_cross_ability
 */

#include "cross_ability.h"
#include "mcp_provider.h"
#include "vnc_provider.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* helpers                                                             */
/* ------------------------------------------------------------------ */
static int tests_run = 0;
static int tests_passed = 0;

#define RUN(fn)                                                        \
    do {                                                               \
        tests_run++;                                                   \
        printf("  %-50s ", #fn);                                       \
        fn();                                                          \
        tests_passed++;                                                \
        printf("PASS\n");                                              \
    } while (0)

/* ------------------------------------------------------------------ */
/* tests: plugin manager                                               */
/* ------------------------------------------------------------------ */

static void test_manager_init(void) {
    assert(cross_ability_manager_init() == CROSS_ABILITY_OK);
    assert(cross_ability_provider_count() == 0);
    cross_ability_manager_shutdown();
}

static void test_register_provider(void) {
    cross_ability_manager_init();
    cross_ability_provider_t *mcp = mcp_provider_create();
    assert(mcp != NULL);
    assert(cross_ability_register(mcp) == CROSS_ABILITY_OK);
    assert(cross_ability_provider_count() == 1);
    cross_ability_manager_shutdown();
}

static void test_register_null(void) {
    cross_ability_manager_init();
    assert(cross_ability_register(NULL) == CROSS_ABILITY_ERR_NO_PROVIDER);
    cross_ability_manager_shutdown();
}

static void test_get_provider(void) {
    cross_ability_manager_init();
    cross_ability_provider_t *mcp = mcp_provider_create();
    cross_ability_register(mcp);
    cross_ability_provider_t *found =
        cross_ability_get_provider(PROVIDER_TYPE_MCP);
    assert(found == mcp);
    assert(cross_ability_get_provider(PROVIDER_TYPE_VNC) == NULL);
    cross_ability_manager_shutdown();
}

static void test_shutdown_clears(void) {
    cross_ability_manager_init();
    cross_ability_provider_t *mcp = mcp_provider_create();
    cross_ability_register(mcp);
    cross_ability_manager_shutdown();
    assert(cross_ability_provider_count() == 0);
}

/* ------------------------------------------------------------------ */
/* tests: MCP provider                                                 */
/* ------------------------------------------------------------------ */

static void test_mcp_create(void) {
    cross_ability_provider_t *p = mcp_provider_create();
    assert(p != NULL);
    assert(p->type == PROVIDER_TYPE_MCP);
    assert(strcmp(p->name, "mcp") == 0);
    p->destroy(p);
}

static void test_mcp_connect_disabled(void) {
    cross_ability_provider_t *p = mcp_provider_create();
    p->enabled = false;
    cross_ability_conn_params_t params = {
        .host = "127.0.0.1", .port = 3000, .from_mobile = true};
    assert(p->connect(p, &params) == CROSS_ABILITY_ERR_DISABLED);
    p->destroy(p);
}

static void test_mcp_connect_enabled(void) {
    cross_ability_provider_t *p = mcp_provider_create();
    p->enabled = true;
    p->init(p);
    cross_ability_conn_params_t params = {
        .host = "192.168.1.100", .port = 3000, .from_mobile = true};
    assert(p->connect(p, &params) == CROSS_ABILITY_OK);
    p->disconnect(p);
    p->destroy(p);
}

static void test_mcp_tool_call_requires_connect(void) {
    cross_ability_provider_t *p = mcp_provider_create();
    p->enabled = true;
    p->init(p);
    mcp_tool_call_t call = {.tool_name = "test", .arguments_json = "{}"};
    /* Not connected yet — should fail */
    assert(mcp_provider_tool_call(p, &call) == CROSS_ABILITY_ERR_CONNECT);
    p->destroy(p);
}

static void test_mcp_tool_call_after_connect(void) {
    cross_ability_provider_t *p = mcp_provider_create();
    p->enabled = true;
    p->init(p);
    cross_ability_conn_params_t params = {
        .host = "127.0.0.1", .port = 3000, .from_mobile = true};
    p->connect(p, &params);
    mcp_tool_call_t call = {
        .tool_name = "list_files", .arguments_json = "{\"path\":\"/\"}"};
    assert(mcp_provider_tool_call(p, &call) == CROSS_ABILITY_OK);
    p->disconnect(p);
    p->destroy(p);
}

/* ------------------------------------------------------------------ */
/* tests: VNC provider                                                 */
/* ------------------------------------------------------------------ */

static void test_vnc_create(void) {
    cross_ability_provider_t *p = vnc_provider_create();
    assert(p != NULL);
    assert(p->type == PROVIDER_TYPE_VNC);
    assert(strcmp(p->name, "vnc") == 0);
    p->destroy(p);
}

static void test_vnc_connect_disabled(void) {
    cross_ability_provider_t *p = vnc_provider_create();
    p->enabled = false;
    cross_ability_conn_params_t params = {
        .host = "192.168.1.200", .port = 5900, .from_mobile = true};
    assert(p->connect(p, &params) == CROSS_ABILITY_ERR_DISABLED);
    p->destroy(p);
}

static void test_vnc_connect_enabled(void) {
    cross_ability_provider_t *p = vnc_provider_create();
    p->enabled = true;
    p->init(p);
    cross_ability_conn_params_t params = {
        .host = "192.168.1.200", .port = 5900, .from_mobile = true};
    assert(p->connect(p, &params) == CROSS_ABILITY_OK);
    p->disconnect(p);
    p->destroy(p);
}

static void test_vnc_send_requires_connect(void) {
    cross_ability_provider_t *p = vnc_provider_create();
    p->enabled = true;
    p->init(p);
    uint8_t data[] = {0x01, 0x02};
    assert(p->send(p, data, sizeof(data)) == CROSS_ABILITY_ERR_CONNECT);
    p->destroy(p);
}

/* ------------------------------------------------------------------ */
/* tests: full integration                                             */
/* ------------------------------------------------------------------ */

static void test_full_flow(void) {
    cross_ability_manager_init();

    cross_ability_provider_t *mcp = mcp_provider_create();
    mcp->enabled = true;
    cross_ability_register(mcp);

    cross_ability_provider_t *vnc = vnc_provider_create();
    vnc->enabled = true;
    cross_ability_register(vnc);

    assert(cross_ability_provider_count() == 2);

    cross_ability_conn_params_t mcp_params = {
        .host = "10.0.0.1", .port = 3000, .from_mobile = true};
    assert(mcp->connect(mcp, &mcp_params) == CROSS_ABILITY_OK);

    cross_ability_conn_params_t vnc_params = {
        .host = "10.0.0.2", .port = 5900, .from_mobile = true};
    assert(vnc->connect(vnc, &vnc_params) == CROSS_ABILITY_OK);

    mcp_tool_call_t call = {
        .tool_name = "run_command", .arguments_json = "{\"cmd\":\"ls\"}"};
    assert(mcp_provider_tool_call(mcp, &call) == CROSS_ABILITY_OK);

    cross_ability_manager_shutdown();
}

/* ------------------------------------------------------------------ */
/* main                                                                */
/* ------------------------------------------------------------------ */

int main(void) {
    printf("cross_ability tests\n");

    RUN(test_manager_init);
    RUN(test_register_provider);
    RUN(test_register_null);
    RUN(test_get_provider);
    RUN(test_shutdown_clears);

    RUN(test_mcp_create);
    RUN(test_mcp_connect_disabled);
    RUN(test_mcp_connect_enabled);
    RUN(test_mcp_tool_call_requires_connect);
    RUN(test_mcp_tool_call_after_connect);

    RUN(test_vnc_create);
    RUN(test_vnc_connect_disabled);
    RUN(test_vnc_connect_enabled);
    RUN(test_vnc_send_requires_connect);

    RUN(test_full_flow);

    printf("\n%d/%d tests passed\n", tests_passed, tests_run);
    return tests_passed == tests_run ? 0 : 1;
}
