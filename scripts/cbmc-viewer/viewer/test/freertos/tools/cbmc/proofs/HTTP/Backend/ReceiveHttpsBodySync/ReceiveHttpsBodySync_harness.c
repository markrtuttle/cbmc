/* FreeRTOS includes. */
#include "FreeRTOS.h"
#include "queue.h"
#include "FreeRTOS_Sockets.h"

/* FreeRTOS+TCP includes. */
#include "iot_https_client.h"
#include "iot_https_internal.h"

#include "global_state_HTTP.h"

// function under test
IotHttpsReturnCode_t _receiveHttpsBodySync( _httpsResponse_t * pHttpsResponse );

void harness() {

  IotHttpsResponseHandle_t resp = allocate_IotResponseHandle();
  __CPROVER_assume(resp);
  initialize_IotResponseHandle(resp);
  __CPROVER_assume(is_valid_IotResponseHandle(resp));

  __CPROVER_assume(!resp->isAsync);
  __CPROVER_assume(resp->pHttpsConnection);
  __CPROVER_assume(resp->pHttpsConnection->pNetworkInterface);
  __CPROVER_assume(IS_STUBBED_NETWORKIF_RECEIVEUPTO(resp->pHttpsConnection->pNetworkInterface));
  __CPROVER_assume(resp->pHttpsConnection->pNetworkConnection);

  // allow a null body pointer (a valid response handle has a valid pointer)
  resp->pBody = nondet_bool() ? NULL : resp->pBody;

  _receiveHttpsBodySync( resp );
}
