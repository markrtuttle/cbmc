#include "global_state_HTTP.h"

/****************************************************************/

/* Implementation of safe malloc which returns NULL if the requested
 * size is 0.  Warning: The behavior of malloc(0) is platform
 * dependent.  It is possible for malloc(0) to return an address
 * without allocating memory.
 */
void *safeMalloc(size_t xWantedSize) {
  return nondet_bool() ? malloc(xWantedSize) : NULL;
}

/****************************************************************
 * HTTP parser stubs
 ****************************************************************/

/* Model the third party HTTP Parser. */
size_t http_parser_execute (http_parser *parser,
                            const http_parser_settings *settings,
                            const char *data,
                            size_t len) {
  __CPROVER_assert(parser, "http_parser_execute parser nonnull");
  __CPROVER_assert(settings, "http_parser_execute settings nonnull");
  __CPROVER_assert(data, "http_parser_execute data nonnull");

  _httpsResponse_t *_httpsResponse = (_httpsResponse_t *)(parser->data);
  // Choose whether the parser found the header
  _httpsResponse->foundHeaderField = nondet_bool();
  _httpsResponse->parserState = PARSER_STATE_BODY_COMPLETE;

  // Generate the header value found
  size_t valueLength;
  if (_httpsResponse->foundHeaderField) {
    __CPROVER_assume(valueLength <= len);
    _httpsResponse->pReadHeaderValue = malloc(valueLength+1);
    _httpsResponse->pReadHeaderValue[valueLength] = 0;
    _httpsResponse->readHeaderValueLength = valueLength;
  }

  // Return the number of characters in ReadHeaderValue
  return _httpsResponse->foundHeaderField ? valueLength : 0;
}

/****************************************************************
 * IotHttpsClientCallbacks: user callbacks
 ****************************************************************/

void CBMCappendHeaderCallback( void * pPrivData,
			       IotHttpsRequestHandle_t reqHandle ) {
  assert(pPrivData);
  assert(reqHandle);
}
void CBMCwriteCallback( void * pPrivData,
			IotHttpsRequestHandle_t reqHandle )
{
  assert(pPrivData);
  assert(reqHandle);
}

void CBMCreadReadyCallback( void * pPrivData,
			    IotHttpsResponseHandle_t respHandle,
			    IotHttpsReturnCode_t rc,
			    uint16_t status ) {
  assert(pPrivData);
  assert(respHandle);
}
void CBMCresponseCompleteCallback( void * pPrivData,
				   IotHttpsResponseHandle_t respHandle,
				   IotHttpsReturnCode_t rc,
				   uint16_t status ) {
  assert(pPrivData);
  assert(respHandle);
}
void CBMCconnectionClosedCallback( void * pPrivData,
				   IotHttpsConnectionHandle_t connHandle,
				   IotHttpsReturnCode_t rc ) {
  assert(pPrivData);
  assert(connHandle);
}
void CBMCerrorCallback( void * pPrivData,
			IotHttpsRequestHandle_t reqHandle,
			IotHttpsResponseHandle_t respHandle,
			IotHttpsReturnCode_t rc ) {
  assert(pPrivData);
  assert(reqHandle);
  assert(respHandle);
}

IotHttpsClientCallbacks_t *allocate_IotClientCallbacks() {
  IotHttpsClientCallbacks_t *pCallbacks =
    safeMalloc(sizeof(IotHttpsClientCallbacks_t));
  return pCallbacks;
}

int is_stubbed_IotClientCallbacks(IotHttpsClientCallbacks_t *pCallbacks) {
  return
    IS_STUBBED_APPENDHEADERCALLBACK(pCallbacks) &&
    IS_STUBBED_WRITECALLBACK(pCallbacks) &&
    IS_STUBBED_READREADYCALLBACK(pCallbacks) &&
    IS_STUBBED_RESPONSECOMPLETECALLBACK(pCallbacks) &&
    IS_STUBBED_CONNECTIONCLOSEDCALLBACK(pCallbacks) &&
    IS_STUBBED_ERRORCALLBACK(pCallbacks);
}

/****************************************************************
 * IotNetworkInterface constructor
 ****************************************************************/

IotNetworkError_t IotNetworkInterfaceCreate( void * pConnectionInfo,
					     void * pCredentialInfo,
					     void * pConnection ) {
  __CPROVER_assert(pConnectionInfo,
		   "IotNetworkInterfaceCreate pConnectionInfo");
  /* create accepts NULL credentials when there is no TLS configuration. */
  __CPROVER_assert(pConnection, "IotNetworkInterfaceCreate pConnection");

  /* The network connection created by this function is an opaque type
   * that is simply passed to the other network functions we are
   * stubbing out, so we just ensure that it points to a memory
   * object. */
  *(char **)pConnection = malloc(1); /* network connection is opaque.  */

  IotNetworkError_t error;
  return error;
}

size_t IotNetworkInterfaceSend_iteration;

size_t IotNetworkInterfaceSend( void * pConnection,
				const uint8_t * pMessage,
				size_t messageLength ) {
  __CPROVER_assert(pConnection, "IotNetworkInterfaceSend pConnection");
  __CPROVER_assert(pMessage, "IotNetworkInterfaceSend pMessage");

  size_t size;
  __CPROVER_assume(size <= messageLength);

  size_t current_iteration = IotNetworkInterfaceSend_iteration;

  if (IotNetworkInterfaceSend_iteration >= 2) {
    size = messageLength;
    IotNetworkInterfaceSend_iteration = 0;
    return size;
  }

  if (size >= messageLength) {
    IotNetworkInterfaceSend_iteration = 0;
    return size;
  }

  IotNetworkInterfaceSend_iteration++;

  return size;
}

IotNetworkError_t IotNetworkInterfaceClose( void * pConnection ) {
  __CPROVER_assert(pConnection, "IotNetworkInterfaceClose pConnection");

  IotNetworkError_t error;
  return error;
}

size_t IotNetworkInterfaceReceive( void * pConnection,
				   uint8_t * pBuffer,
				   size_t bytesRequested ) {
  __CPROVER_assert(pConnection, "IotNetworkInterfaceReceive pConnection");
  __CPROVER_assert(pBuffer, "IotNetworkInterfaceReceive pBuffer");

  /* Fill the entire memory object pointed to by pBuffer with
   * unconstrained data.  This use of __CPROVER_array_copy with a
   * single byte is a common CBMC idiom. */
  uint8_t byte;
  __CPROVER_array_copy(pBuffer,&byte);

  size_t size;
  __CPROVER_assume(size <= bytesRequested);
  return size;
}

size_t IotNetworkInterfaceReceiveUpto( void * pConnection,
				       uint8_t * pBuffer,
				       size_t bytesRequested ) {
  __CPROVER_assert(pConnection, "IotNetworkInterfaceReceiveUpto pConnection");
  __CPROVER_assert(pBuffer, "IotNetworkInterfaceReceiveUpto pBuffer");

  /* Fill the entire memory object pointed to by pBuffer with
   * unconstrained data.  This use of __CPROVER_array_copy with a
   * single byte is a common CBMC idiom. */
  size_t size;
  __CPROVER_assume(size <= bytesRequested);
  return size;
}


IotNetworkError_t IotNetworkInterfaceCallback( void * pConnection,
					       IotNetworkReceiveCallback_t
					         receiveCallback,
					       void * pContext ) {
  __CPROVER_assert(pConnection,
		   "IotNetworkInterfaceCallback pConnection");
  __CPROVER_assert(receiveCallback,
		   "IotNetworkInterfaceCallback receiveCallback");
  __CPROVER_assert(pContext,
		   "IotNetworkInterfaceCallback pContext");

  IotNetworkError_t error;
  return error;
}

IotNetworkError_t IotNetworkInterfaceDestroy( void * pConnection ) {
  __CPROVER_assert(pConnection, "IotNetworkInterfaceDestroy pConnection");

  IotNetworkError_t error;
  return error;
}

/* Models the Network Interface. */
IotNetworkInterface_t *allocate_NetworkInterface() {
  return safeMalloc(sizeof(IotNetworkInterface_t));
}

int is_valid_NetworkInterface(IotNetworkInterface_t *netif) {
  return
    netif->create &&
    netif->close &&
    netif->send &&
    netif->receive &&
    netif->receiveUpto &&
    netif->setReceiveCallback &&
    netif->destroy;
}

/* Use
 *   __CPROVER_assume(is_stubbed_NetworkInterface(netif));
 * to ensure the stubbed out functions are used.  The initializer for
 * IOTNI appears to be ignored when CBMC is run with
 * --nondet-static. */

int is_stubbed_NetworkInterface(IotNetworkInterface_t *netif) {
  return
    IS_STUBBED_NETWORKIF_CREATE(netif) &&
    IS_STUBBED_NETWORKIF_CLOSE(netif) &&
    IS_STUBBED_NETWORKIF_SEND(netif) &&
    IS_STUBBED_NETWORKIF_RECEIVE(netif) &&
    IS_STUBBED_NETWORKIF_RECEIVEUPTO(netif) &&
    IS_STUBBED_NETWORKIF_SETRECEIVECALLBACK(netif) &&
    IS_STUBBED_NETWORKIF_DESTROY(netif);
}

/****************************************************************
 * IotHttpsConnectionInfo constructor
 ****************************************************************/

/* Creates a Connection Info and assigns memory accordingly. */
IotHttpsConnectionInfo_t * allocate_IotConnectionInfo() {
  IotHttpsConnectionInfo_t * pConnInfo =
    safeMalloc(sizeof(IotHttpsConnectionInfo_t));
  if(pConnInfo) {
    pConnInfo->pNetworkInterface = allocate_NetworkInterface();
    pConnInfo->pAddress = safeMalloc(pConnInfo->addressLen);
    pConnInfo->pAlpnProtocols = safeMalloc(pConnInfo->alpnProtocolsLen);
    pConnInfo->pCaCert = safeMalloc(sizeof(uint32_t));
    pConnInfo->pClientCert = safeMalloc(sizeof(uint32_t));
    pConnInfo->pPrivateKey = safeMalloc(sizeof(uint32_t));
    pConnInfo->userBuffer.pBuffer = safeMalloc(sizeof(struct _httpsConnection));
  }
  return pConnInfo;
}

int is_valid_IotConnectionInfo(IotHttpsConnectionInfo_t *pConnInfo) {
  return
    pConnInfo->pCaCert &&
    pConnInfo->pClientCert &&
    pConnInfo->pPrivateKey &&
    pConnInfo->userBuffer.pBuffer &&
    pConnInfo->pNetworkInterface &&
    is_valid_NetworkInterface(pConnInfo->pNetworkInterface);
}

/****************************************************************
 * IotHttpsConnectionHandle constructor
 ****************************************************************/

/* Creates a Connection Handle and assigns memory accordingly. */
IotHttpsConnectionHandle_t allocate_IotConnectionHandle () {
  IotHttpsConnectionHandle_t pConnectionHandle =
    safeMalloc(sizeof(struct _httpsConnection));
  if(pConnectionHandle) {
    // network connection just points to an allocated memory object
    pConnectionHandle->pNetworkConnection = safeMalloc(1);
    pConnectionHandle->pNetworkInterface = allocate_NetworkInterface();
  }
  return pConnectionHandle;
}

void
initialize_IotConnectionHandle (IotHttpsConnectionHandle_t
				pConnectionHandle) {
  if(pConnectionHandle) {
    IotListDouble_Create(&pConnectionHandle->reqQ);
    IotListDouble_Create(&pConnectionHandle->respQ);
    // Add zero or one element to response queue
    if (nondet_bool()) {
      IotHttpsResponseHandle_t resp = allocate_IotResponseHandle();
      __CPROVER_assume(resp);
      // Testing synchronous API!!
      __CPROVER_assume(!resp->isAsync);
      initialize_IotResponseHandle(resp);
      __CPROVER_assume(is_valid_IotResponseHandle(resp));
      IotListDouble_InsertHead(&pConnectionHandle->respQ, &resp->link);
    }
    // Add zero or one element to request queue
    if (nondet_bool()) {
      IotHttpsRequestHandle_t req = allocate_IotRequestHandle();
      __CPROVER_assume(req);
      __CPROVER_assume(req->pHttpsConnection);
      __CPROVER_assume(req->pHttpsResponse);
      // Testing synchronous API!!
      __CPROVER_assume(!req->isAsync);
      initialize_IotRequestHandle(req);
      __CPROVER_assume(is_valid_IotRequestHandle(req));
      IotListDouble_InsertHead(&pConnectionHandle->reqQ, &req->link);
    }
 }
}

int is_valid_IotConnectionHandle(IotHttpsConnectionHandle_t handle) {
  return
    handle->pNetworkConnection &&
    handle->pNetworkInterface &&
    is_valid_NetworkInterface(handle->pNetworkInterface);
}

/****************************************************************
 * IotHttpsResponseHandle constructor
 ****************************************************************/

/* Creates a Response Handle and assigns memory accordingly. */
IotHttpsResponseHandle_t allocate_IotResponseHandle() {
  IotHttpsResponseHandle_t pResponseHandle =
    safeMalloc(sizeof(struct _httpsResponse));
  if(pResponseHandle) {
    size_t headerLen;
    size_t bodyLen;
    pResponseHandle->pHeaders = safeMalloc(headerLen);
    pResponseHandle->pBody = safeMalloc(bodyLen);
    pResponseHandle->pHttpsConnection = allocate_IotConnectionHandle();
    pResponseHandle->pReadHeaderField =
      safeMalloc(pResponseHandle->readHeaderFieldLength);
    pResponseHandle->pReadHeaderValue =
      safeMalloc(pResponseHandle->readHeaderValueLength);
    pResponseHandle->pCallbacks = allocate_IotClientCallbacks();
    pResponseHandle->pUserPrivData = safeMalloc(1);
  }
  return pResponseHandle;
}

// ???: Should be is_stubbed
void
initialize_IotResponseHandle(IotHttpsResponseHandle_t pResponseHandle) {
  if(pResponseHandle) {
    // Initialization of httpParserInfo done by _initializeResponse
    pResponseHandle->httpParserInfo.parseFunc = http_parser_execute;
    pResponseHandle->httpParserInfo.readHeaderParser.data = (void *) pResponseHandle;
    pResponseHandle->httpParserInfo.responseParser.data = (void *) pResponseHandle;
    // Do we need a more complete model of queued requests and responses?
    __CPROVER_assume(!pResponseHandle->link.pPrevious);
    __CPROVER_assume(!pResponseHandle->link.pNext);
  }
}

int is_valid_IotResponseHandle(IotHttpsResponseHandle_t pResponseHandle) {
  int required1 =
    __CPROVER_same_object(pResponseHandle->pHeaders,
			  pResponseHandle->pHeadersCur) &&
    __CPROVER_same_object(pResponseHandle->pHeaders,
			  pResponseHandle->pHeadersEnd);
  int required2 =
    __CPROVER_same_object(pResponseHandle->pBody,
			  pResponseHandle->pBodyCur) &&
    __CPROVER_same_object(pResponseHandle->pBody,
			  pResponseHandle->pBodyEnd);
  if (!required1 || !required2) return 0;

  int valid_headers =
    pResponseHandle->pHeaders != NULL;
  int valid_header_order =
    pResponseHandle->pHeaders <= pResponseHandle->pHeadersCur &&
    pResponseHandle->pHeadersCur <=  pResponseHandle->pHeadersEnd;
  int valid_body =
    pResponseHandle->pBody != NULL;
  int valid_body_order =
    pResponseHandle->pBody <= pResponseHandle->pBodyCur &&
    pResponseHandle->pBodyCur <=  pResponseHandle->pBodyEnd;
  int valid_parserdata =
    pResponseHandle->httpParserInfo.readHeaderParser.data == pResponseHandle;
  int bounded_header_buffer =
    __CPROVER_OBJECT_SIZE(pResponseHandle->pHeaders) < CBMC_MAX_OBJECT_SIZE;
  int bounded_body_buffer =
    __CPROVER_OBJECT_SIZE(pResponseHandle->pBody) < CBMC_MAX_OBJECT_SIZE;
  int bounded_field_buffer =
    __CPROVER_OBJECT_SIZE(pResponseHandle->pReadHeaderField) < CBMC_MAX_OBJECT_SIZE;
  int bounded_value_buffer =
    __CPROVER_OBJECT_SIZE(pResponseHandle->pReadHeaderValue) < CBMC_MAX_OBJECT_SIZE;
  return
    valid_headers &&
    valid_header_order &&
    valid_body &&
    valid_body_order &&
    valid_parserdata &&
    bounded_header_buffer &&
    bounded_body_buffer &&
    bounded_field_buffer &&
    bounded_value_buffer &&
    // valid_order and short circuit evaluation prevents integer overflow
    __CPROVER_r_ok(pResponseHandle->pHeaders,
		   pResponseHandle->pHeadersEnd - pResponseHandle->pHeaders) &&
    __CPROVER_w_ok(pResponseHandle->pHeaders,
		   pResponseHandle->pHeadersEnd - pResponseHandle->pHeaders) &&
    __CPROVER_r_ok(pResponseHandle->pBody,
		   pResponseHandle->pBodyEnd - pResponseHandle->pBody) &&
    __CPROVER_w_ok(pResponseHandle->pBody,
		   pResponseHandle->pBodyEnd - pResponseHandle->pBody);
}

/****************************************************************
 * IotHttpsRequestHandle constructor
 ****************************************************************/

/* Creates a Request Handle and assigns memory accordingly. */
IotHttpsRequestHandle_t allocate_IotRequestHandle() {
  IotHttpsRequestHandle_t pRequestHandle =
    safeMalloc(sizeof(struct _httpsRequest));
  if (pRequestHandle) {
    uint32_t headerLen;
    pRequestHandle->pHttpsResponse = allocate_IotResponseHandle();
    pRequestHandle->pHttpsConnection = allocate_IotConnectionHandle();
    pRequestHandle->pHeaders = safeMalloc(headerLen);
    pRequestHandle->pBody = safeMalloc(pRequestHandle->bodyLength);
    pRequestHandle->pConnInfo = allocate_IotConnectionInfo();
  }
  return pRequestHandle;
}

void
initialize_IotRequestHandle(IotHttpsRequestHandle_t pRequestHandle) {
  if(pRequestHandle) {
    __CPROVER_assume(!pRequestHandle->link.pPrevious);
    __CPROVER_assume(!pRequestHandle->link.pNext);
    if(pRequestHandle->pHttpsResponse) {
      initialize_IotResponseHandle(pRequestHandle->pHttpsResponse);
    }
  }
}

int is_valid_IotRequestHandle(IotHttpsRequestHandle_t pRequestHandle) {
  int required =
    __CPROVER_same_object(pRequestHandle->pHeaders,
			  pRequestHandle->pHeadersCur) &&
    __CPROVER_same_object(pRequestHandle->pHeaders,
			  pRequestHandle->pHeadersEnd);
  if (!required) return 0;

  int valid_headers =
    pRequestHandle->pHeaders != NULL;
  int valid_order =
    pRequestHandle->pHeaders <= pRequestHandle->pHeadersCur &&
    pRequestHandle->pHeadersCur <=  pRequestHandle->pHeadersEnd;
  int valid_body =
    pRequestHandle->pBody != NULL;
  int bounded_header_buffer =
    __CPROVER_OBJECT_SIZE(pRequestHandle->pHeaders) < CBMC_MAX_OBJECT_SIZE;
  int bounded_body_buffer =
    __CPROVER_OBJECT_SIZE(pRequestHandle->pBody) < CBMC_MAX_OBJECT_SIZE;
  return
    valid_headers &&
    valid_order &&
    valid_body &&
    bounded_header_buffer &&
    bounded_body_buffer &&
    // valid_order and short circuit evaluation prevents integer overflow
    __CPROVER_r_ok(pRequestHandle->pHeaders,
		   pRequestHandle->pHeadersEnd - pRequestHandle->pHeaders) &&
    __CPROVER_w_ok(pRequestHandle->pHeaders,
		   pRequestHandle->pHeadersEnd - pRequestHandle->pHeaders);
}

/****************************************************************
 * IotHttpsRequestInfo constructor
 * This is currently unusued and untested.
 ****************************************************************/

/* Creates a Request Info and assigns memory accordingly. */
IotHttpsRequestInfo_t * allocate_IotRequestInfo() {
  IotHttpsRequestInfo_t * pReqInfo
    = safeMalloc(sizeof(IotHttpsRequestInfo_t));
  if(pReqInfo) {
    pReqInfo->userBuffer.pBuffer = safeMalloc(pReqInfo->userBuffer.bufferLen);
    pReqInfo->pHost = safeMalloc(pReqInfo->hostLen);
  }
  return pReqInfo;
}

int is_valid_IotRequestInfo(IotHttpsRequestInfo_t * pReqInfo) {
  return
    pReqInfo->hostLen <= IOT_HTTPS_MAX_HOST_NAME_LENGTH + 1;
}

/****************************************************************
 * IotHttpsResponseInfo constructor
 ****************************************************************/

/* Creates a Response Info and assigns memory accordingly. */
IotHttpsResponseInfo_t * allocate_IotResponseInfo() {
  IotHttpsResponseInfo_t * pRespInfo =
    safeMalloc(sizeof(IotHttpsResponseInfo_t));
  if(pRespInfo) {
    pRespInfo->userBuffer.pBuffer = safeMalloc(pRespInfo->userBuffer.bufferLen);
    pRespInfo->pSyncInfo = safeMalloc(sizeof(IotHttpsSyncInfo_t));
    if (pRespInfo->pSyncInfo)
      pRespInfo->pSyncInfo->pBody = safeMalloc(pRespInfo->pSyncInfo->bodyLen);
  }
  return pRespInfo;
}

int is_valid_IotResponseInfo(IotHttpsResponseInfo_t * pRespInfo){
  return
    pRespInfo->pSyncInfo &&
    pRespInfo->pSyncInfo->pBody &&
    pRespInfo->pSyncInfo->bodyLen <= CBMC_MAX_OBJECT_SIZE &&
    pRespInfo->userBuffer.bufferLen <= CBMC_MAX_OBJECT_SIZE;
}
