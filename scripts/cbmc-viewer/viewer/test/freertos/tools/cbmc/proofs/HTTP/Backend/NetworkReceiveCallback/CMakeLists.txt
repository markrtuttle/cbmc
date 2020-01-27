set(ENTRY NetworkReceiveCallback)
list(APPEND test_labels ${ENTRY})

set(FREERTOS ${CMAKE_SOURCE_DIR})
set(PROOF ${CMAKE_SOURCE_DIR}/tools/cbmc)

set(CBMC_OBJECTID_BITS 8)

################################################################

set(PROJECT_SOURCE
    ${FREERTOS}/libraries/c_sdk/standard/https/src/iot_https_client.c
)

set(PROJECT_REMOVE
    # validated independently
    --remove-function-body IotHttpsClient_Disconnect
    --remove-function-body _receiveHttpsBodyAsync
    --remove-function-body _receiveHttpsBodySync
    --remove-function-body _receiveHttpsHeaders

    # _sendHttpsRequest is used only as an argument to the function
    # IotTaskPool_CreateJob that we are abstracting in this proof.
    # _sendHttpsRequest will appear in the list of functions with
    # missing function bodies even though it is not being called.
    --remove-function-body _sendHttpsRequest

    # unused function
    --remove-function-body IotHttpsClient_Init
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
     _flushHttpsNetworkData.0:2
)

################################################################

include(../HTTP.cmake)

