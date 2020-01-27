H_PRV_UNLOCK_UNWINDING_BOUND = 4
H_QueueSemaphoreTake_BOUND = 4
H_ENTRY = QueueTakeMutexRecursive
H_CBMCFLAGS = --unwind 4 --unwindset prvUnlockQueue.0:4,prvUnlockQueue.1:4 --signed-overflow-check --pointer-overflow-check --unsigned-overflow-check
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/queue.goto $(FREERTOS)/freertos_kernel/list.goto $(FREERTOS)/tools/cbmc/proofs/CBMCStubLibrary/tasksStubs.goto
H_DEF = -DconfigUSE_TRACE_FACILITY=0 -DconfigGENERATE_RUN_TIME_STATS=0 -DPRV_UNLOCK_UNWINDING_BOUND=4 -DQueueSemaphoreTake_BOUND=4
H_INC = -I.
H_GENERATE_HEADER = queue_datastructure.h
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common