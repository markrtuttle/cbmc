* Reduce the number of source files marked up
	* Add utility to generate a json list of source files used
	  (generate by building with the preprocessor and scanning the
	  result for source files; this solves the problem of multiple
	  builds giving conflicting symbol definitions).  Include sloc
	  data in the summary.
	* Use json list of source files as list of files to markup

* Improve accuracy of linking symbols to definitions
	* Add utility to generate json list of symbols definitions using
	  ctags instead of etags.
	* Use json list of source files as list of files to search for symbols
	* Modify markup to ignore comments and strings when looking for
	  strings to link to symbol definitions.

* Simplify coverage markup
    * Add utility to generate a json summary of coverage checking.

* Improve trace markup
	* Add utility to generate a json summary of property checking.
	* Major issue is that json output from CBMC is hard to translate
	  into a simple representation, and the json output does not include
	  the ascii string produced by the text output.

* Use CSS files for markup instead of hardcoded, inlined style attributes.

* Use a template engine or markup generator to produce html output.

* Cleanup error handling in tags.py and block.py.



Architecture plans:

CBMC must produce cbmc.json, coverage.json, properties.json since these
require knowing the cbmc arguments.

make-sources (from blddir with make, find, or xwalk)
make-symbols (from made sources)
make-coverage (from cbmc output)
make-results (from cbmc output)
make-traces (from cbmc output)
make-loops
make-properties
make-reachable

make-report takes all of this to generate the report
cbmc-viewer is a script invoking these functions

Generally, make_x.make_x returns a (metadata, data) pair where metadata is
the timestamp, arguments, and argument timestamps if relevant.  And make-x
invokes make_x.make_x and dumps json of {metadata, data}.  Then the xt.py
module reads in this stuff and does all the rendering required by make-report.


make-sources - done
make-symbols - done (moved to exuberant ctags)
do comments
do css
then do remainder slowly




Goal:

markup contains ALL html markup instructions
  this is our html generator

report produces top level report
traces produces traces
loops produces loops
tree produces source tree

sourcet manages source files from make-sources (from build, walk, find)
symbolt manages symbols from make-symbols
coveraget manages coverage from make-coverage (from xml, json)
resultt manages pass/fail results from make-results (from txt)
tracet manages traces from make-traces (from txt)
  use source to markup source locations
loopt manages loops from make-loops (from goto binary)
propertyt manages properties from make-properties (from xml or json)
reachablet manages reachable functions from make-reachable

