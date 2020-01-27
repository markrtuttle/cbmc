H_ENTRY = QueueSemaphoreTake
H_QUEUE_BOUND = 5
H_CBMCFLAGS = --unwind 2 --signed-overflow-check --pointer-overflow-check --unsigned-overflow-check --nondet-static --unwindset prvUnlockQueue.0:5,prvUnlockQueue.1:5,xQueueSemaphoreTake.0:3
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/queue.goto $(FREERTOS)/freertos_kernel/list.goto $(FREERTOS)/tools/cbmc/proofs/CBMCStubLibrary/tasksStubs.goto
H_DEF = -DconfigUSE_TRACE_FACILITY=0 -DconfigGENERATE_RUN_TIME_STATS=0 -DPRV_UNLOCK_QUEUE_BOUND=5
H_INC = -I.
H_GENERATE_HEADER = queue_datastructure.h
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common