/* FreeRTOS includes. */
#include "FreeRTOS.h"
#include "queue.h"
#include "FreeRTOS_Sockets.h"

/* FreeRTOS+TCP includes. */
#include "iot_https_client.h"
#include "iot_https_internal.h"

#include "global_state_HTTP.h"

// function under test
void _networkReceiveCallback( void * pNetworkConnection,
			      void * pReceiveContext );

void harness() {
  // This parameter is irrelevant (unused by the function)
  size_t pNetworkConnection_size;
  void *pNetworkConnection = safeMalloc(pNetworkConnection_size);

  // pReceiveContext
  IotHttpsConnectionHandle_t pReceiveContext = allocate_IotConnectionHandle();
  __CPROVER_assume(pReceiveContext);
  initialize_IotConnectionHandle(pReceiveContext);
  __CPROVER_assume(is_valid_IotConnectionHandle(pReceiveContext));
  __CPROVER_assume(IS_STUBBED_NETWORKIF_CLOSE(pReceiveContext->pNetworkInterface));
  __CPROVER_assume(IS_STUBBED_NETWORKIF_RECEIVEUPTO(pReceiveContext->pNetworkInterface));
  __CPROVER_assume(IS_STUBBED_NETWORKIF_DESTROY(pReceiveContext->pNetworkInterface));

  _networkReceiveCallback(pNetworkConnection, (void *)pReceiveContext);
}
