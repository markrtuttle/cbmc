set(ENTRY SendHttpsRequest)
list(APPEND test_labels ${ENTRY})

set(FREERTOS ${CMAKE_SOURCE_DIR})
set(PROOF ${CMAKE_SOURCE_DIR}/tools/cbmc)

################################################################

set(PROJECT_SOURCE
    ${FREERTOS}/libraries/c_sdk/standard/https/src/iot_https_client.c
)

set(PROJECT_REMOVE
    # verified independently
    --remove-function-body IotHttpsClient_Disconnect

    # stubbed in harness
    --remove-function-body __builtin___memcpy_chk
    --remove-function-body memcpy

    # unused functions influencing function pointer removal
    --remove-function-body IotHttpsClient_Init
    --remove-function-body _networkReceiveCallback
)

################################################################

set(HARNESS_SOURCE
    ${PROOF}/proofs/HTTP/global_state_HTTP.c
    ${CMAKE_CURRENT_SOURCE_DIR}/${ENTRY}_harness.c
)

set(HARNESS_REMOVE
    # unused functions influencing function pointer removal
    --remove-function-body is_stubbed_IotClientCallbacks
    --remove-function-body is_stubbed_NetworkInterface
)

################################################################

set(UNWINDSET
     _networkSend.0:4
)

################################################################

include(../HTTP.cmake)
