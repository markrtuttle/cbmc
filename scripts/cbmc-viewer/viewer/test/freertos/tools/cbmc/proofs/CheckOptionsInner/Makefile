H_ENTRY = CheckOptionsInner
H_BUFFER_SIZE = 100
H_CBMCFLAGS = --unwind 1 --unwindset prvTCPWindowTxCheckAck.1:2,prvTCPWindowFastRetransmit.2:2
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_TCP_IP.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_TCP_WIN.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_Stream_Buffer.goto $(FREERTOS)/freertos_kernel/tasks.goto $(FREERTOS)/freertos_kernel/list.goto
H_DEF = -DBUFFER_SIZE=100
H_EXPECTED = SUCCESSFUL

include ../Makefile.common