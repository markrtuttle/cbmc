H_ENTRY = DNSgetHostByName_cancel
H_callback = 1
H_MAX_HOSTNAME_LEN = 10
H_HOSTNAME_UNWIND = 11
H_CBMCFLAGS = --unwind 1 --unwindset prvProcessDNSCache.0:5,strlen.0:11,__builtin___strcpy_chk.0:11,vDNSCheckCallBack.0:2,strcpy.0:11 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DNS.goto $(FREERTOS)/freertos_kernel/tasks.goto $(FREERTOS)/freertos_kernel/list.goto
H_DEF = -DipconfigDNS_USE_CALLBACKS=1 -DMAX_HOSTNAME_LEN=10
H_OPT = -m32
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common