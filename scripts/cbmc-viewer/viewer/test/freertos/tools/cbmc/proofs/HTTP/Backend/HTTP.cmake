if(NOT DEFINED CBMC_OBJECTID_BITS)
  # don't cache this value so it can be overridden by the proof.
  set(CBMC_OBJECTID_BITS 7)
endif()
set(CBMC_MAX_OBJECT_SIZE "(UINT32_MAX>>CBMC_OBJECTID_BITS)" CACHE STRING "help")

set(INC
    ${FREERTOS}/demos/include
    ${FREERTOS}/freertos_kernel/include
    ${FREERTOS}/freertos_kernel/portable/MSVC-MingW
    ${FREERTOS}/libraries/3rdparty/http_parser
    ${FREERTOS}/libraries/3rdparty/jsmn
    ${FREERTOS}/libraries/3rdparty/mbedtls/include/mbedtls
    ${FREERTOS}/libraries/3rdparty/pkcs11
    ${FREERTOS}/libraries/3rdparty/tinycbor
    ${FREERTOS}/libraries/3rdparty/tracealyzer_recorder/Include
    ${FREERTOS}/libraries/3rdparty/win_pcap
    ${FREERTOS}/libraries/abstractions/platform/freertos/include/
    ${FREERTOS}/libraries/abstractions/platform/include/
    ${FREERTOS}/libraries/c_sdk/aws/defender/include
    ${FREERTOS}/libraries/c_sdk/standard/common/include/
    ${FREERTOS}/libraries/c_sdk/standard/https/include
    ${FREERTOS}/libraries/c_sdk/standard/https/src/private
    ${FREERTOS}/libraries/c_sdk/standard/serializer/src/cbor
    ${FREERTOS}/libraries/freertos_plus/aws/ota/include
    ${FREERTOS}/libraries/freertos_plus/standard/freertos_plus_tcp/include
    ${FREERTOS}/libraries/freertos_plus/standard/freertos_plus_tcp/source/portable/BufferManagement
    ${FREERTOS}/libraries/freertos_plus/standard/freertos_plus_tcp/source/portable/Compiler/MSVC
    ${FREERTOS}/vendors/pc/boards/windows/aws_demos/application_code
    ${FREERTOS}/vendors/pc/boards/windows/aws_demos/config_files

    ${PROOF}/include
    ${PROOF}/windows
    ${PROOF}/proofs/HTTP
)

set(DEF
    WINVER=0x400
    _CONSOLE
    _CRT_SECURE_NO_WARNINGS
    _DEBUG
    _WIN32_WINNT=0x0500
    __PRETTY_FUNCTION__=__FUNCTION__
    __free_rtos__

    CBMC
    CBMC_OBJECTID_BITS=${CBMC_OBJECTID_BITS}
    CBMC_MAX_OBJECT_SIZE=${CBMC_MAX_OBJECT_SIZE}
)

set(CFLAGS
    -m32
)

set(UNWIND 1)

################################################################

add_executable(
    ${ENTRY}1.goto
    ${PROJECT_SOURCE}
)

set_target_properties(
    ${ENTRY}1.goto
    PROPERTIES
    INCLUDE_DIRECTORIES      "${INC}"
    COMPILE_DEFINITIONS      "${DEF}"
    COMPILE_OPTIONS          "${CFLAGS}"
)

list(PREPEND PROJECT_REMOVE goto-instrument)
list(APPEND  PROJECT_REMOVE ${ENTRY}1.goto)
list(APPEND  PROJECT_REMOVE ${ENTRY}1a.goto)

################################################################

add_executable(
    ${ENTRY}2.goto
    ${HARNESS_SOURCE}
)

set_target_properties(
    ${ENTRY}2.goto
    PROPERTIES
    INCLUDE_DIRECTORIES      "${INC}"
    COMPILE_DEFINITIONS      "${DEF}"
    COMPILE_OPTIONS          "${CFLAGS}"
)

list(PREPEND HARNESS_REMOVE goto-instrument)
list(APPEND  HARNESS_REMOVE ${ENTRY}2.goto)
list(APPEND  HARNESS_REMOVE ${ENTRY}2a.goto)

################################################################

add_custom_command(
    DEPENDS ${ENTRY}1.goto ${ENTRY}2.goto
    OUTPUT ${ENTRY}1a.goto ${ENTRY}2a.goto
    	   ${ENTRY}3.goto ${ENTRY}4.goto
           ${ENTRY}5.goto ${ENTRY}.goto
    COMMENT "Linking"
    COMMAND ${PROJECT_REMOVE}
    COMMAND ${HARNESS_REMOVE}
    COMMAND
      goto-cc --function harness ${ENTRY}1a.goto ${ENTRY}2a.goto -o ${ENTRY}3.goto
    COMMAND
      goto-instrument --add-library ${ENTRY}3.goto ${ENTRY}4.goto
    COMMAND
      goto-instrument --drop-unused-functions ${ENTRY}4.goto ${ENTRY}5.goto
    COMMAND
      goto-instrument --slice-global-inits ${ENTRY}5.goto ${ENTRY}.goto
)

add_custom_target(${ENTRY} ALL DEPENDS ${ENTRY}.goto)

################################################################

# Append a bogus loop in case unwindset is empty
list(APPEND UNWINDSET "UNWINDSET:1")
list(JOIN UNWINDSET "," _UNWINDSET)

set(_cbmc_flags
    --32
    --object-bits ${CBMC_OBJECTID_BITS}
    --bounds-check
    --pointer-check
    --div-by-zero-check
    --float-overflow-check
    --nan-check
    --pointer-overflow-check
    --undefined-shift-check
    --signed-overflow-check
    --unsigned-overflow-check
    --nondet-static
    --unwind ${UNWIND}
    --unwindset ${_UNWINDSET}
)

list(JOIN _cbmc_flags " " cbmc_flags)

################################################################

add_test(
  NAME ${ENTRY}-cbmc
  COMMAND /bin/sh -c
    "cbmc --unwinding-assertions --trace ${cbmc_flags} ${ENTRY}.goto > cbmc.txt 2>&1 "
)

set_tests_properties(
    ${ENTRY}-cbmc
    PROPERTIES
    LABELS "${test_labels}"
    SKIP_RETURN_CODE 10
)

add_test(
  NAME ${ENTRY}-property
  COMMAND /bin/sh -c
    "cbmc --unwinding-assertions --show-properties ${cbmc_flags} ${ENTRY}.goto --xml-ui > property.xml 2>&1"
)

set_tests_properties(
    ${ENTRY}-property
    PROPERTIES
    LABELS "${test_labels}"
)

add_test(
  NAME ${ENTRY}-coverage
  COMMAND /bin/sh -c
    "cbmc --cover location ${cbmc_flags} ${ENTRY}.goto --xml-ui > coverage.xml 2>&1"
)

set_tests_properties(
    ${ENTRY}-coverage
    PROPERTIES
    LABELS "${test_labels}"
)

set(_report_command
    cbmc-viewer
    --goto ${ENTRY}.goto
    --srcdir ${FREERTOS}
    --blddir ${FREERTOS}
    --htmldir ${CMAKE_BINARY_DIR}/results/${ENTRY}
    --srcexclude "\"(./doc|./tests|./vendors)\""
    --result cbmc.txt
    --property property.xml
    --block coverage.xml
    --config ${CMAKE_CURRENT_SOURCE_DIR}/cbmc-viewer.py
)
list(JOIN _report_command " " report_command)

add_test(
  NAME ${ENTRY}-report
  COMMAND /bin/sh -c "${report_command}"
)

set_tests_properties(
    ${ENTRY}-report
    PROPERTIES
    LABELS "${test_labels}"
    DEPENDS "${ENTRY}-cbmc;${ENTRY}-property;${ENTRY}-coverage"
)

################################################################

