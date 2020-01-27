H_ENTRY = TaskStartScheduler
H_DEF = -DFREERTOS_MODULE_TEST -D'mtCOVERAGE_TEST_MARKER()=__CPROVER_assert(1, "Coverage marker")' -DconfigUSE_TRACE_FACILITY=0 -DconfigGENERATE_RUN_TIME_STATS=0
H_CBMCFLAGS = --unwind 1 --unwindset prvInitialiseTaskLists.0:8,prvInitialiseNewTask.0:16,prvInitialiseNewTask.1:4
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/tasks.goto $(FREERTOS)/freertos_kernel/list.goto $(FREERTOS)/freertos_kernel/timers.goto $(FREERTOS)/freertos_kernel/queue.goto
H_INC = -I$(FREERTOS)/tools/cbmc/proofs/TaskPool/TaskStartScheduler/
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common