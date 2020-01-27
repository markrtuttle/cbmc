set(ENTRY ReceiveHttpsBodyAsync)
list(APPEND test_labels ${ENTRY})

set(FREERTOS ${CMAKE_SOURCE_DIR})
set(PROOF ${CMAKE_SOURCE_DIR}/tools/cbmc)

################################################################

set(PROJECT_SOURCE
    ${FREERTOS}/libraries/c_sdk/standard/https/src/iot_https_client.c
)

set(PROJECT_REMOVE
)

################################################################

set(HARNESS_SOURCE
    ${PROOF}/proofs/HTTP/global_state_HTTP.c
    ${CMAKE_CURRENT_SOURCE_DIR}/${ENTRY}_harness.c
)

set(HARNESS_REMOVE
    # unused functions influencing function pointer removal
    --remove-function-body is_stubbed_IotClientCallbacks
)

################################################################

set(UNWINDSET
)

################################################################

include(../HTTP.cmake)
