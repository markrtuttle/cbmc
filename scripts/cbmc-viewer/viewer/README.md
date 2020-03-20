The viewer tool summarizes the results of cbmc as a collection of
annotated error report, trace files, and source files linked together
as a collection of html pages.

Preliminary documentation is available with 'viewer --help'.

Read the code in the following order (respecting module dependencies
illustrated in README.png):

runt.py
locationt.py
parse.py

sourcet.py
make-sources

symbolt.py
make-symbols

resultt.py
make-results

tracet.py
make-traces

coveratet.py
make-coverage

propertyt.py
make-property

loopt.py
make-loop

markupt.py
markup\_tracet.py
markup\_report.py
markup\_sourcet.py

reachable.py

viewconfig.py
viewer
