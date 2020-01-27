/* FreeRTOS includes. */
#include "FreeRTOS.h"
#include "queue.h"
#include "FreeRTOS_Sockets.h"

/* FreeRTOS+TCP includes. */
#include "iot_https_client.h"
#include "iot_https_internal.h"

#include "global_state_HTTP.h"

// function under test
IotHttpsReturnCode_t _receiveHttpsHeaders( _httpsConnection_t * pHttpsConnection,
					   _httpsResponse_t * pHttpsResponse );

void harness() {
  IotHttpsConnectionHandle_t conn = allocate_IotConnectionHandle();
  __CPROVER_assume(conn);
  initialize_IotConnectionHandle(conn);
  __CPROVER_assume(is_valid_IotConnectionHandle(conn));

  __CPROVER_assume(conn->pNetworkInterface);
  __CPROVER_assume(IS_STUBBED_NETWORKIF_RECEIVEUPTO(conn->pNetworkInterface));

  IotHttpsResponseHandle_t resp = allocate_IotResponseHandle();
  __CPROVER_assume(resp);
  initialize_IotResponseHandle(resp);
  __CPROVER_assume(is_valid_IotResponseHandle(resp));

  __CPROVER_assume(!resp->isAsync);
  __CPROVER_assume(resp->pHttpsConnection);
  __CPROVER_assume(resp->pHttpsConnection->pNetworkInterface);
  __CPROVER_assume(IS_STUBBED_NETWORKIF_RECEIVEUPTO(resp->pHttpsConnection->pNetworkInterface));

  _receiveHttpsHeaders(conn, resp);
}
