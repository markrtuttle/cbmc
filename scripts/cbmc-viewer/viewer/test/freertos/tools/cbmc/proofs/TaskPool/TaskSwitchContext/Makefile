H_ENTRY = TaskSwitchContext
H_DEF = -DFREERTOS_MODULE_TEST -D'portGET_HIGHEST_PRIORITY(uxTopPriority, uxReadyPriorities)=__CPROVER_assume( uxTopPriority < configMAX_PRIORITIES )' -D'mtCOVERAGE_TEST_MARKER()=__CPROVER_assert(1, "Coverage marker")'
H_CBMCFLAGS = --unwind 1 --unwindset prvInitialiseTaskLists.0:8,xPrepareTaskLists.0:8,vListInsert.0:2
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/tasks.goto $(FREERTOS)/freertos_kernel/list.goto
H_INC = -I$(FREERTOS)/tools/cbmc/proofs/TaskPool/TaskSwitchContext/
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common