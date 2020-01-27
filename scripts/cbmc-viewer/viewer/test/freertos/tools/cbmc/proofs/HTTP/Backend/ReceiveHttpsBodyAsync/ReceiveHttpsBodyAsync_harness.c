/* FreeRTOS includes. */
#include "FreeRTOS.h"
#include "queue.h"
#include "FreeRTOS_Sockets.h"

/* FreeRTOS+TCP includes. */
#include "iot_https_client.h"
#include "iot_https_internal.h"

#include "global_state_HTTP.h"

IotHttpsReturnCode_t _receiveHttpsBodyAsync( _httpsResponse_t * pHttpsResponse );

void harness() {
  IotHttpsResponseHandle_t resp = allocate_IotResponseHandle();
  __CPROVER_assume(resp);
  initialize_IotResponseHandle(resp);
  __CPROVER_assume(is_valid_IotResponseHandle(resp));

  __CPROVER_assume(resp->isAsync);

  __CPROVER_assume(resp->pCallbacks);
  __CPROVER_assume(IS_STUBBED_READREADYCALLBACK(resp->pCallbacks));
  __CPROVER_assume(resp->pUserPrivData); // context for callbacks.

  _receiveHttpsBodyAsync( resp );
}
