H_ENTRY = ProcessReceivedUDPPacket
H_MAX_RX_PACKETS = 1
H_USE_LLMNR = 1
H_USE_NBNS = 1
H_CBMCFLAGS = --unwind 1 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_UDP_IP.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_IP.goto
H_DEF = -DipconfigUDP_MAX_RX_PACKETS=1 -DipconfigUSE_LLMNR=1 -DipconfigUSE_NBNS=1
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common