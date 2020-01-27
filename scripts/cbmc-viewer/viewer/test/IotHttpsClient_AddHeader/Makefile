default: coverage loops properties sources results traces

clean:
	$(RM) *-*.json

ENTRY=IotHttpsClient_AddHeader
FREERTOS=../freertos
ADD_HEADER=../freertos/tools/cbmc/proofs/HTTP/$(ENTRY)

################################################################
# Coverage

MAKE_COVERAGE=../../make-coverage

coverage: coverage-json coverage-xml
	diff coverage-json.json coverage-xml.json

coverage-json:
	$(MAKE_COVERAGE) --root $(FREERTOS) --json coverage.json > coverage-json.json

coverage-xml:
	$(MAKE_COVERAGE) --root $(FREERTOS) --xml coverage.xml > coverage-xml.json

################################################################
# Loops

MAKE_LOOPS=../../make-loops

loops: loops-json loops-xml loops-goto
	diff loops-json.json loops-xml.json
	diff loops-json.json loops-goto.json
	diff {.,output}/loops-json.json
	diff {.,output}/loops-xml.json
	diff {.,output}/loops-goto.json

loops-goto:
	$(MAKE_LOOPS) --root $(FREERTOS) --goto IotHttpsClient_AddHeader.goto > loops-goto.json


loops-json:
	$(MAKE_LOOPS) --root $(FREERTOS) --json loops.json > loops-json.json

loops-xml:
	$(MAKE_LOOPS) --root $(FREERTOS) --xml loops.xml > loops-xml.json


################################################################
# Properties

MAKE_PROPERTY=../../make-properties

property properties: property-json property-xml
	diff property-json.json property-xml.json
	diff {.,output}/property-json.json
	diff {.,output}/property-xml.json

property-json:
	$(MAKE_PROPERTY) --root $(FREERTOS) --json property.json > property-json.json

property-xml:
	$(MAKE_PROPERTY) --root $(FREERTOS) --xml property.xml > property-xml.json

################################################################
# Results

MAKE_RESULTS=../../make-results
COMPARE_RESULTS=../compare-results

results: results-txt results-json results-xml
	diff {.,output}/results-txt.json
	diff {.,output}/results-json.json
	diff {.,output}/results-xml.json
	python3 $(COMPARE_RESULTS) results-txt.json results-json.json results-xml.json

results-txt:
	$(MAKE_RESULTS) --root $(FREERTOS) --text cbmc.txt > results-txt.json

results-json:
	$(MAKE_RESULTS) --root $(FREERTOS) --json cbmc.json > results-json.json

results-xml:
	$(MAKE_RESULTS) --root $(FREERTOS) --xml cbmc.xml > results-xml.json


################################################################
# Traces

MAKE_TRACES=../../make-traces
COMPARE_TRACES=../compare-traces

traces: traces-txt traces-json traces-xml
	diff {.,output}/traces-txt.json
	diff {.,output}/traces-json.json
	diff {.,output}/traces-xml.json
	python3 $(COMPARE_TRACES) traces-txt.json traces-json.json traces-xml.json

traces-txt:
	$(MAKE_TRACES) --root $(FREERTOS) --wkdir $(ADD_HEADER) --text cbmc.txt > traces-txt.json

traces-json:
	$(MAKE_TRACES) --root $(FREERTOS) --json cbmc.json > traces-json.json

traces-xml:
	$(MAKE_TRACES) --root $(FREERTOS) --xml cbmc.xml > traces-xml.json

################################################################
# Sources

MAKE_SOURCES=../../make-sources
COMPARE_SOURCES=../compare-sources

sources: sources-build sources-find sources-walk
	diff {.,output}/sources-build.json
	diff {.,output}/sources-find.json
	diff {.,output}/sources-walk.json
	python3 $(COMPARE_SOURCES) sources-build.json sources-find.json sources-walk.json

sources-build:
	$(MAKE_SOURCES) --root $(FREERTOS) --build $(ADD_HEADER) > sources-build.json

sources-find:
	$(MAKE_SOURCES) --root $(FREERTOS) --find > sources-find.json

sources-walk:
	$(MAKE_SOURCES) --root $(FREERTOS) --walk > sources-walk.json

################################################################
# Symbols

MAKE_SYMBOLS=../../make-symbols

symbols: symbols-build symbols-find symbols-walk
	diff symbols-find.json symbols-walk.json
	diff {.,output}/symbols-build.json
	diff {.,output}/symbols-find.json
	diff {.,output}/symbols-walk.json

symbols-build:
	$(MAKE_SYMBOLS) --root $(FREERTOS) --sources sources-build.json > symbols-build.json

symbols-find:
	$(MAKE_SYMBOLS) --root $(FREERTOS) --sources sources-find.json > symbols-find.json

symbols-walk:
	$(MAKE_SYMBOLS) --root $(FREERTOS) --sources sources-walk.json > symbols-walk.json


################################################################

VIEWER=../../viewer
viewer:
	$(VIEWER) \
	--goto $(ENTRY).goto \
	--srcdir $(FREERTOS) \
	--blddir $(ADD_HEADER) \
	--htmldir html \
	--srcexclude "(./doc|./tests|./vendors)" \
	--cbmc-result cbmc.txt \
	--cbmc-property property.xml \
	--cbmc-coverage coverage.xml $(VERBOSE)
