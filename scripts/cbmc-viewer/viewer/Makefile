default:
	@echo Nothing to make

pylint:
	pylint --disable=duplicate-code,missing-docstring --module-rgx '[\w-]+' *.py make-* viewer

symbols:
	make-symbols --root ../../freertos/lib/  --exclude ./third_party

coverage:
	make-coverage --root ../../freertos/lib/  --data coverage.json

results:
	make-results --root ../../freertos/lib/  --data cbmc.json

loops:
	make-loops --root ../../freertos/lib/  --data loops.json

properties:
	make-properties --root ../../freertos --data property.json


clean:
	rm *~
