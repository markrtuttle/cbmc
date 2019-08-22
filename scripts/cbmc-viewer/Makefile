################################################################

pylint:
	-pylint cbmc-viewer *.py make-sources make-symbols \
		--disable=duplicate-code,invalid-name

################################################################

clean:
	$(RM) *.pyc
	$(RM) *~ .*~ \#* .\#*

################################################################

.PHONY: pylint clean
