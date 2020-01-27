H_ENTRY = TCPReturnPacket
H_RX_MESSAGES = 1
H_CBMCFLAGS = --unwind 1 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_TCP_IP.goto
H_DEF = -DipconfigUSE_LINKED_RX_MESSAGES=1 -DFREERTOS_TCP_ENABLE_VERIFICATION
H_INC = -I$(FREERTOS)/tools/cbmc/include
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common