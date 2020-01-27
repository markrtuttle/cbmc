H_ENTRY = QueueCreateCountingSemaphoreStatic
H_CBMCFLAGS = --unwind 1 --signed-overflow-check --pointer-overflow-check --unsigned-overflow-check
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/queue.goto $(FREERTOS)/freertos_kernel/list.goto
H_DEF = -DconfigUSE_TRACE_FACILITY=0 -DconfigGENERATE_RUN_TIME_STATS=0
H_GENERATE_HEADER = queue_datastructure.h
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common