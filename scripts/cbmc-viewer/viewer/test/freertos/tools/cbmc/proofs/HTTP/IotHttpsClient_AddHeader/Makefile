H_ENTRY = IotHttpsClient_AddHeader
H_CBMC_OBJECTID_BITS = 7
H_CBMC_MAX_OBJECT_SIZE = "((UINT32_MAX>>CBMC_OBJECTID_BITS)>>1)"
H_CBMCFLAGS = --unwind 1 --unwindset strlen.0:5,strncmp.0:20 --nondet-static --div-by-zero-check --float-overflow-check --nan-check --pointer-overflow-check --undefined-shift-check --signed-overflow-check --unsigned-overflow-check
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/c_sdk/standard/https/src/iot_https_client.goto
H_INSTFLAGS = --remove-function-body IotLogError
H_INC = -I$(FREERTOS)/libraries/c_sdk/standard/https/include -I$(FREERTOS)/libraries/c_sdk/standard/https/src/private -I$(FREERTOS)/libraries/3rdparty/http_parser -I$(FREERTOS)/libraries/c_sdk/standard/common/include/ -I$(FREERTOS)/libraries/abstractions/platform/include/ -I$(FREERTOS)/libraries/abstractions/platform/freertos/include/ -I../../include
H_DEF = -DCBMC_OBJECTID_BITS=7 -DCBMC_MAX_OBJECT_SIZE="((UINT32_MAX>>CBMC_OBJECTID_BITS)>>1)"
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common