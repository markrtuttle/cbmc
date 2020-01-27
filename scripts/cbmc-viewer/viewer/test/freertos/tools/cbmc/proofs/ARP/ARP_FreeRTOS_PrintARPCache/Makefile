H_ENTRY = FreeRTOS_PrintARPCache
H_CBMCFLAGS = --unwind 7 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_ARP.goto
H_DEF = -DipconfigARP_CACHE_ENTRIES=6
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common