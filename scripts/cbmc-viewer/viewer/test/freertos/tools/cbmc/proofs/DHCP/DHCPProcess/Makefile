H_ENTRY = DHCPProcess
H_CBMCFLAGS = --unwind 4 --unwindset strlen.0:11,memcmp.0:7,prvProcessDHCPReplies.0:8 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DHCP.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_IP.goto $(FREERTOS)/freertos_kernel/tasks.goto
H_BUFFER_SIZE = 299
H_DEF = -DBUFFER_SIZE=299
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common