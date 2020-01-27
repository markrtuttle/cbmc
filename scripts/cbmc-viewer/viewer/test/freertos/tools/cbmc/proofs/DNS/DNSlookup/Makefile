H_ENTRY = DNSlookup
H_MAX_HOSTNAME_LEN = 255
H_HOSTNAME_UNWIND = 256
H_USE_CACHE = 1
H_CBMCFLAGS = --unwind 1 --unwindset prvProcessDNSCache.0:5,strcmp.0:256 --nondet-static
H_OBJS = $(ENTRY)_harness.goto $(FREERTOS)/libraries/freertos_plus/standard/freertos_plus_tcp/source/FreeRTOS_DNS.goto $(FREERTOS)/freertos_kernel/tasks.goto
H_DEF = -DipconfigUSE_DNS_CACHE=1 -DMAX_HOSTNAME_LEN=255
H_OPT = -m32
H_EXPECTED = SUCCESSFUL

include ../../Makefile.common