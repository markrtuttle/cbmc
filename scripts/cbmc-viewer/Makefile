################################################################

PYLINT = \
	*.py \
	cbmc-viewer \
	make-sources \
	make-symbols \
	make-traces \

pylint:
	-pylint $(PYLINT) \
		--disable=duplicate-code,invalid-name

pylint-quiet:
	-pylint $(PYLINT) \
		--disable=duplicate-code,invalid-name,missing-docstring,too-many-arguments,too-many-branches,too-many-statements

################################################################

clean:
	$(RM) *.pyc
	$(RM) *~ .*~ \#* .\#*

################################################################

.PHONY: pylint clean
