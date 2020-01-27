H_ENTRY = ProcessReceivedTCPPacket
H_CBMCFLAGS = --unwind 1 --unwindset prvTCPSendRepeated.0:13 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_TCP_IP.goto
H_INSTFLAGS = --remove-function-body prvSingleStepTCPHeaderOptions --remove-function-body prvCheckOptions --remove-function-body prvTCPPrepareSend --remove-function-body prvTCPReturnPacket --remove-function-body prvTCPHandleState
H_DEF = -DFREERTOS_TCP_ENABLE_VERIFICATION
H_INC = -I$(FREERTOS)/tools/cbmc/include
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common