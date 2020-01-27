H_ENTRY = DNSgetHostByName_a
H_callback = 1
H_MAX_HOSTNAME_LEN = 10
H_MAX_REQ_SIZE = 50
H_HOSTNAME_UNWIND = 11
H_CBMCFLAGS = --unwind 1 --unwindset prvCreateDNSMessage.0:11,prvCreateDNSMessage.1:11,prvGetHostByName.0:11,prvProcessDNSCache.0:5,strlen.0:11,__builtin___strcpy_chk.0:11,strcmp.0:11,xTaskResumeAll.0:11,xTaskResumeAll.1:11,strcpy.0:11 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DNS.goto $(FREERTOS)/freertos_kernel/tasks.goto
H_DEF = -DipconfigDNS_USE_CALLBACKS=1 -DMAX_HOSTNAME_LEN=10 -DMAX_REQ_SIZE=50
H_OPT = -m32
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common