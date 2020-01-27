H_ENTRY = ProcessDHCPReplies
H_BUFFER_SIZE = 300
H_BUFFER_HEADER = 241
H_BUFFER_PAYLOAD = 61
H_CBMCFLAGS = --unwind 1 --unwindset memcmp.0:7,prvProcessDHCPReplies.0:61
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DHCP.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/portable/BufferManagement/BufferAllocation_2.goto $(FREERTOS)/freertos_kernel/event_groups.goto $(FREERTOS)/freertos_kernel/list.goto
H_DEF = -DBUFFER_SIZE=300
H_EXPECTED = SUCCESSFUL

include ../Makefile.common