"""The statically reachable functions."""

import json
import re

import runt
import locationt

class Reachable:
    """The statically reachable functions.
    """

    def __init__(self, pgm, location=None):
        """Initialize the statically reachable functions."""

        # get reachable functions
        jsons = runt.run(["goto-analyzer", "--reachable-functions",
                          "--json", "-", pgm])
        # the json produced by goto-analyzer is preceeded by a block of text
        jsons = re.sub(r'^.*\n\[', '[', jsons, flags=re.DOTALL)
        # the json produced by goto-analyzer sometimes omits line numbers
        jsons = jsons.replace('"first line": ,\n', '"first line": 0,\n')
        jsons = jsons.replace('"last line": \n', '"last line": 0\n')

        self.functions = {}
        for function in json.loads(jsons):
            name = function['function']
            path = locationt.canonical(function['file name'])

            if name.startswith('__CPROVER'):
                continue
            if not path.startswith(location.blddir):
                continue
            if locationt.builtin_name(path):
                continue

            path = locationt.canonical_childpath(path, location.blddir)
            self.functions[path] = self.functions.get(path, set())
            self.functions[path].add(name)

        for path, functions in self.functions.items():
            self.functions[path] = sorted(functions)

    def dump(self):
        return json.dumps({'reachable-functions': self.functions}, indent=2)

################################################################
