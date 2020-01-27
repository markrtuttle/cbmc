H_ENTRY = TCPHandleState
H_TX_DRIVER = 1
H_RX_MESSAGES = 1
H_CBMCFLAGS = --unwind 1 --unwindset prvWinScaleFactor.0:2 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_TCP_IP.goto
H_DEF = -DipconfigZERO_COPY_TX_DRIVER=1 -DipconfigUSE_LINKED_RX_MESSAGES=1 -DFREERTOS_TCP_ENABLE_VERIFICATION
H_INSTFLAGS = --remove-function-body prvTCPPrepareSend --remove-function-body prvTCPReturnPacket
H_INC = -I$(FREERTOS)/tools/cbmc/include
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common