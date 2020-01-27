#ifndef GLOBAL_STATE_HTTP
#define GLOBAL_STATE_HTTP

#include "iot_https_client.h"
#include "iot_https_internal.h"

/*****************************************************************/

void *safeMalloc(size_t xWantedSize);

/****************************************************************
 * IotHttpsConnectionHandle
 ****************************************************************/

IotHttpsConnectionHandle_t allocate_IotConnectionHandle ();
int is_valid_IotConnectionHandle(IotHttpsConnectionHandle_t handle);
void initialize_IotConnectionHandle (IotHttpsConnectionHandle_t
				     pConnectionHandle);

/****************************************************************
 * IotHttpsConnectionInfo
 ****************************************************************/

IotHttpsConnectionInfo_t * allocate_IotConnectionInfo();
int is_valid_IotConnectionInfo(IotHttpsConnectionInfo_t *pConnInfo);

/****************************************************************
 * IotHttpsResponseHandle
 ****************************************************************/

IotHttpsResponseHandle_t allocate_IotResponseHandle();
int is_valid_IotResponseHandle(IotHttpsResponseHandle_t pResponseHandle);
void initialize_IotResponseHandle(IotHttpsResponseHandle_t pResponseHandle);

/****************************************************************
 * IotHttpsResponseInfo
 ****************************************************************/

IotHttpsResponseInfo_t * allocate_IotResponseInfo();
int is_valid_IotResponseInfo(IotHttpsResponseInfo_t * pRespInfo);

/****************************************************************
 * IotHttpsRequestHandle
 ****************************************************************/

IotHttpsRequestHandle_t allocate_IotRequestHandle();
int is_valid_IotRequestHandle(IotHttpsRequestHandle_t pRequestHandle);
void initialize_IotRequestHandle(IotHttpsRequestHandle_t pRequestHandle);

/****************************************************************
 * IotHttpsRequestInfo
 ****************************************************************/

IotHttpsRequestInfo_t * allocate_IotRequestInfo();
int is_valid_IotRequestInfo(IotHttpsRequestInfo_t * pReqInfo);

/****************************************************************
 * IotClientCallbacks
 ****************************************************************/

IotHttpsClientCallbacks_t *allocate_IotClientCallbacks();
int is_stubbed_IotClientCallbacks(IotHttpsClientCallbacks_t *pCallbacks);

#define IS_STUBBED_APPENDHEADERCALLBACK(cb) \
  (cb->appendHeaderCallback == CBMCappendHeaderCallback)
#define IS_STUBBED_WRITECALLBACK(cb) \
  (cb->writeCallback == CBMCwriteCallback)
#define IS_STUBBED_READREADYCALLBACK(cb) \
  (cb->readReadyCallback == CBMCreadReadyCallback)
#define IS_STUBBED_RESPONSECOMPLETECALLBACK(cb) \
  (cb->responseCompleteCallback == CBMCresponseCompleteCallback)
#define IS_STUBBED_CONNECTIONCLOSEDCALLBACK(cb) \
  (cb->connectionClosedCallback == CBMCconnectionClosedCallback)
#define IS_STUBBED_ERRORCALLBACK(cb) \
  (cb->errorCallback == CBMCerrorCallback)

// The callback stubs
void CBMCappendHeaderCallback( void * pPrivData,
			       IotHttpsRequestHandle_t reqHandle );
void CBMCwriteCallback( void * pPrivData,
			IotHttpsRequestHandle_t reqHandle );
void CBMCreadReadyCallback( void * pPrivData,
			    IotHttpsResponseHandle_t respHandle,
			    IotHttpsReturnCode_t rc,
			    uint16_t status );
void CBMCresponseCompleteCallback( void * pPrivData,
				   IotHttpsResponseHandle_t respHandle,
				   IotHttpsReturnCode_t rc,
				   uint16_t status );
void CBMCconnectionClosedCallback( void * pPrivData,
				   IotHttpsConnectionHandle_t connHandle,
				   IotHttpsReturnCode_t rc );
void CBMCerrorCallback( void * pPrivData,
			IotHttpsRequestHandle_t reqHandle,
			IotHttpsResponseHandle_t respHandle,
			IotHttpsReturnCode_t rc );

/****************************************************************
 * IotNetworkInterface
 ****************************************************************/

IotNetworkInterface_t *allocate_NetworkInterface();
int is_valid_NetworkInterface(IotNetworkInterface_t *netif);
int is_stubbed_NetworkInterface(IotNetworkInterface_t *netif);

#define IS_STUBBED_NETWORKIF_CREATE(netif) \
  (netif->create == IotNetworkInterfaceCreate)
#define IS_STUBBED_NETWORKIF_CLOSE(netif) \
  (netif->close == IotNetworkInterfaceClose)
#define IS_STUBBED_NETWORKIF_SEND(netif) \
  (netif->send == IotNetworkInterfaceSend)
#define IS_STUBBED_NETWORKIF_RECEIVE(netif) \
  (netif->receive == IotNetworkInterfaceReceive)
#define IS_STUBBED_NETWORKIF_RECEIVEUPTO(netif) \
  (netif->receiveUpto == IotNetworkInterfaceReceiveUpto)
#define IS_STUBBED_NETWORKIF_SETRECEIVECALLBACK(netif) \
  (netif->setReceiveCallback == IotNetworkInterfaceCallback)
#define IS_STUBBED_NETWORKIF_DESTROY(netif) \
  (netif->destroy == IotNetworkInterfaceDestroy)

IotNetworkError_t
IotNetworkInterfaceCreate( void * pConnectionInfo,
			   void * pCredentialInfo,
			   void * pConnection );
size_t
IotNetworkInterfaceSend( void * pConnection,
			 const uint8_t * pMessage,
			 size_t messageLength );
IotNetworkError_t
IotNetworkInterfaceClose( void * pConnection );
size_t
IotNetworkInterfaceReceive( void * pConnection,
			    uint8_t * pBuffer,
			    size_t bytesRequested );
size_t
IotNetworkInterfaceReceiveUpto( void * pConnection,
				uint8_t * pBuffer,
				size_t bytesRequested );
IotNetworkError_t
IotNetworkInterfaceCallback( void * pConnection,
			     IotNetworkReceiveCallback_t receiveCallback,
			     void * pContext );
IotNetworkError_t
IotNetworkInterfaceDestroy( void * pConnection );

/*****************************************************************
 * Third-party http parser methods are stubbed out.
 ****************************************************************/

size_t http_parser_execute (http_parser *parser,
                            const http_parser_settings *settings,
                            const char *data,
                            size_t len);

#endif

