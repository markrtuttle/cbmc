H_ENTRY = ReadNameField
H_NETWORK_BUFFER_SIZE = 10
H_NAME_SIZE = 10
H_READLOOP0 = prvReadNameField.0
H_READLOOP0_UNWIND = 10
H_READLOOP1 = prvReadNameField.1
H_READLOOP1_UNWIND = 10
H_CBMCFLAGS = --unwind 1 --unwindset prvReadNameField.0:10,prvReadNameField.1:10
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DNS.goto
H_DEF = -DNETWORK_BUFFER_SIZE=10 -DNAME_SIZE=10
H_EXPECTED = SUCCESSFUL

include ../Makefile.common