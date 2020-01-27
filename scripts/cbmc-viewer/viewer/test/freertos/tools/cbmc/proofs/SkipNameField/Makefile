H_ENTRY = SkipNameField
H_NETWORK_BUFFER_SIZE = 10
H_SKIPLOOP0 = prvSkipNameField.0
H_SKIPLOOP0_UNWIND = 5
H_CBMCFLAGS = --unwind 1 --unwindset prvSkipNameField.0:5
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DNS.goto
H_DEF = -DNETWORK_BUFFER_SIZE=10
H_EXPECTED = SUCCESSFUL

include ../Makefile.common