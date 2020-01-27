H_ENTRY = IotHttpsClient_ReadHeader
H_MAX_ACCEPTED_SIZE = 20
H_STRNCPY_UNWIND = 21
H_CBMC_OBJECTID_BITS = 7
H_CBMC_MAX_OBJECT_SIZE = "(UINT32_MAX>>CBMC_OBJECTID_BITS)"
H_CBMCFLAGS = --unwind 1 --unwindset __builtin___strncpy_chk.0:21,strncpy.0:21 --nondet-static --div-by-zero-check --float-overflow-check --nan-check --pointer-overflow-check --undefined-shift-check --signed-overflow-check --unsigned-overflow-check
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/c_sdk/standard/https/src/iot_https_client.goto
H_INC = -I$(FREERTOS)/libraries/c_sdk/standard/https/include -I$(FREERTOS)/libraries/c_sdk/standard/https/src/private -I$(FREERTOS)/libraries/3rdparty/http_parser -I$(FREERTOS)/libraries/c_sdk/standard/common/include/ -I$(FREERTOS)/libraries/abstractions/platform/include/ -I$(FREERTOS)/libraries/abstractions/platform/freertos/include/ -I../../include
H_DEF = -DMAX_ACCEPTED_SIZE=20 -DCBMC_OBJECTID_BITS=7 -DCBMC_MAX_OBJECT_SIZE="(UINT32_MAX>>CBMC_OBJECTID_BITS)"
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common