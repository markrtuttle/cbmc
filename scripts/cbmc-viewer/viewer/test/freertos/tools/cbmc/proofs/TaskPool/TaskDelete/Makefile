H_ENTRY = TaskDelete
H_DEF = -DFREERTOS_MODULE_TEST -D'mtCOVERAGE_TEST_MARKER()=__CPROVER_assert(1, "Coverage marker")' -DSTACK_DEPTH=10 -DconfigUSE_TRACE_FACILITY=0 -DconfigGENERATE_RUN_TIME_STATS=0
H_CBMCFLAGS = --unwind 1 --unwindset prvInitialiseTaskLists.0:8,vListInsert.0:3
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/tasks.goto $(FREERTOS)/freertos_kernel/list.goto
H_INC = -I$(FREERTOS)/tools/cbmc/proofs/TaskPool/TaskDelete/
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common