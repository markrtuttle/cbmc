H_ENTRY = DNSclear
H_USE_CACHE = 1
H_CBMCFLAGS = --unwind 1 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DNS.goto
H_DEF = -DipconfigUSE_DNS_CACHE=1
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common