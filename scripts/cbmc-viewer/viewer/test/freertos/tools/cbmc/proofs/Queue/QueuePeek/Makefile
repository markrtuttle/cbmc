H_ENTRY = QueuePeek
H_LOCK_BOUND = 4
H_QUEUE_PEEK_BOUND = 4
H_CBMCFLAGS = --unwind 1 --signed-overflow-check --pointer-overflow-check --unsigned-overflow-check --unwindset prvUnlockQueue.0:4,prvUnlockQueue.1:4,xQueuePeek.0:4 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/queue.goto $(FREERTOS)/freertos_kernel/list.goto $(FREERTOS)/tools/cbmc/proofs/CBMCStubLibrary/tasksStubs.goto
H_DEF = -DconfigUSE_TRACE_FACILITY=0 -DconfigGENERATE_RUN_TIME_STATS=0 -DLOCK_BOUND=4 -DQUEUE_PEEK_BOUND=4 -DINCLUDE_xTaskGetSchedulerState=1
H_INC = -I.
H_GENERATE_HEADER = queue_datastructure.h
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common