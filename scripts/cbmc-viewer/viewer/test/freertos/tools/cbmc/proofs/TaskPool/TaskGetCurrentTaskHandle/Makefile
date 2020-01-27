H_ENTRY = TaskGetCurrentTaskHandle
H_DEF = -DFREERTOS_MODULE_TEST -D'mtCOVERAGE_TEST_MARKER()=__CPROVER_assert(1, "Coverage marker")'
H_CBMCFLAGS = --unwind 1
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/tasks.goto $(FREERTOS)/freertos_kernel/list.goto
H_INC = -I$(FREERTOS)/freertos_kernel/ -I$(FREERTOS)/tools/cbmc/proofs/TaskPool/TaskGetCurrentTaskHandle/
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common