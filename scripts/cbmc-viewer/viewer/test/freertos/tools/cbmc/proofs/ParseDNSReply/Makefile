H_ENTRY = ParseDNSReply
H_NETWORK_BUFFER_SIZE = 40
H_PARSELOOP0 = prvParseDNSReply.0
H_PARSELOOP0_UNWIND = 6
H_PARSELOOP1 = prvParseDNSReply.1
H_PARSELOOP1_UNWIND = 12
H_CBMCFLAGS = --unwind 1 --unwindset prvParseDNSReply.0:6,prvParseDNSReply.1:12,prvProcessDNSCache.0:5
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DNS.goto $(FREERTOS)/freertos_kernel/tasks.goto
H_DEF = -DNETWORK_BUFFER_SIZE=40
H_EXPECTED = SUCCESSFUL

include ../Makefile.common