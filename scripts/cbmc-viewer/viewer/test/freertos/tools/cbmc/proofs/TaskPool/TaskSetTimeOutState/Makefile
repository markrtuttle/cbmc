H_ENTRY = TaskSetTimeOutState
H_DEF = -D'mtCOVERAGE_TEST_MARKER()=__CPROVER_assert(1, "Coverage marker")'
H_CBMCFLAGS = --unwind 1
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/freertos_kernel/tasks.goto
H_INC = -I$(FREERTOS)/tools/cbmc/proofs/TaskPool/TaskSetTimeOutState/
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common