H_ENTRY = QueueReceive
H_LOCK_BOUND = 2
H_QUEUE_RECEIVE_BOUND = 3
H_CBMCFLAGS = --unwind 1 --signed-overflow-check --pointer-overflow-check --unsigned-overflow-check --unwindset xQueueReceive.0:3,prvUnlockQueue.0:2,prvUnlockQueue.1:2 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/queue.goto $(FREERTOS)/freertos_kernel/list.goto $(FREERTOS)/tools/cbmc/proofs/CBMCStubLibrary/tasksStubs.goto
H_DEF = -DconfigUSE_TRACE_FACILITY=0 -DconfigGENERATE_RUN_TIME_STATS=0 -DINCLUDE_xTaskGetSchedulerState=1 -DQUEUE_RECEIVE_BOUND=3 -DLOCK_BOUND=2
H_INC = -I.
H_GENERATE_HEADER = queue_datastructure.h
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common