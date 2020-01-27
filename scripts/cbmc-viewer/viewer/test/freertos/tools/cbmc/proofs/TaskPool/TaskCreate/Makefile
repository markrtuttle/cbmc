H_ENTRY = TaskCreate
H_DEF = -DSTACK_DEPTH=10 -DFREERTOS_MODULE_TEST -D'mtCOVERAGE_TEST_MARKER()=__CPROVER_assert(1, "Coverage marker")'
H_CBMCFLAGS = --unwind 1 --unwindset prvInitialiseNewTask.0:16,prvInitialiseNewTask.1:4,prvInitialiseTaskLists.0:8
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/tasks.goto $(FREERTOS)/freertos_kernel/list.goto
H_INC = -I$(FREERTOS)/tools/cbmc/proofs/TaskPool/TaskCreate/
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common