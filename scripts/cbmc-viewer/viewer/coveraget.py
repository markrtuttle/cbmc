"""CBMC coverage data"""

import json
import logging
import re

import locationt
import parse

class Coverage:
    """Manage CBMC coverage data."""

    def __init__(self,
                 coverage=None,
                 txtfile=None, xmlfile=None, jsonfile=None,
                 root=None):
        """Load CBMC coverage data.

        Load the data from a json file, or parse the xml or json
        coverage output from CBMC generated 'cbmc --cover location'.
        If a souce root is given, make all paths under this root
        relative paths relative to this root.
        """
        logging.debug("Coverage: coverage=%s xmlfile=%s jsonfile=%s root=%s",
                      coverage, xmlfile, jsonfile, root)

        if txtfile:
            raise UserWarning("Text files not allowed for coverage data.")

        # coverage: path -> func -> line -> {'hit', 'missed', 'both'}
        self.coverage = {}
        # line_coverage: path -> line -> {'hit', 'missed', 'both'}
        self.line_coverage = {}
        # function_summary: path -> func -> (percentage, hit, total)
        self.function_summary = {}
        # summary: (percentage, hit, total)
        self.summary = (0, 0, 0)

        if coverage:
            with open(coverage) as load:
                self.coverage = fix_line_numbers(json.load(load)['coverage'])
        elif jsonfile:
            self.coverage, _ = parse_json_coverage(jsonfile, root)
        elif xmlfile:
            self.coverage, _ = parse_xml_coverage(xmlfile, root)
        else:
            print("No coverage data found")
            logging.info("No coverage data found")
            return

        self.line_coverage = compute_line_coverage(self.coverage)
        self.function_summary = compute_function_summary(self.coverage)
        self.summary = compute_summary(self.function_summary)

    def lookup(self, filename, line):
        return self.line_coverage.get(filename, {}).get(line)

    def dump(self):
        return json.dumps({'coverage': self.coverage,
                           'function-summary': self.function_summary,
                           'summary': self.summary}, indent=2)

################################################################

def fix_line_numbers(dct):
    """Integer keys are converted to strings by json.dumps."""

    intkey1 = lambda dct: {int(key): val
                           for key, val in dct.items()}
    intkey2 = lambda dct: {key: intkey1(val)
                           for key, val in dct.items()}
    intkey3 = lambda dct: {key: intkey2(val)
                           for key, val in dct.items()}
    return intkey3(dct)

# line_coverage: path -> line -> {'hit', 'missed', 'both'}
def compute_line_coverage(coverage):
    line_coverage = {}
    for path, func_data in coverage.items():
        line_coverage[path] = {}
        for _, line_data in func_data.items():
            line_coverage[path].update(line_data)
    return line_coverage

# function_summary: path -> func -> (percentage, hit, total)
# BUG: need to restrict to reachable functions
def compute_function_summary(coverage):
    function_summary = {}
    for path, func_data in coverage.items():
        function_summary[path] = {}
        for func, line_data in func_data.items():
            hit = 0
            total = 0
            for _, status in line_data.items():
                hit += 1 if status != 'missed' else 0
                total += 1
            percentage = float(hit)/float(total) if total else 0.0
            function_summary[path][func] = {
                'percentage': percentage,
                'hit': hit,
                'total': total
            }
    return function_summary

# summary: (percentage, hit, total)
def compute_summary(function_summary):
    hit = 0
    total = 0
    for _, func_data in function_summary.items():
        for _, func_summary in func_data.items():
            hit += func_summary['hit']
            total += func_summary['total']
    percentage = float(hit)/float(total) if total else 0.0
    return {
        'percentage': percentage,
        'hit': hit,
        'total': total
    }

################################################################

def update_coverage(coverage, path, func, line, status):
    if coverage.get(path) is None:
        coverage[path] = {}
    if coverage[path].get(func) is None:
        coverage[path][func] = {}
    if coverage[path][func].get(line) is None:
        coverage[path][func][line] = status
    else:
        if coverage[path][func][line] != status:
            coverage[path][func][line] = 'both'
    return coverage

def parse_description(desc):
    def parse_lines(string):
        lines = []
        for line_range in string.split(','):
            bounds = line_range.split('-')
            if len(bounds) == 1:
                lines.append(int(bounds[0]))
            else:
                lines.extend(range(int(bounds[0]), int(bounds[1])))
        return sorted(lines)

    match = re.match(r'block [0-9]+ \(lines (.*)\)', desc)
    if not match:
        logging.debug("Found unparsable coverage description: %s", desc)
        return None, None, None

    # assert one coverage block: covering a single file, no inlining
    assert not ';' in match.group(1)
    block = match.group(1)

    filename, function, lines = block.split(':')
    return filename, function, parse_lines(lines)

def parse_status(status):
    return 'hit' if status.upper() == 'SATISFIED' else 'missed'

def parse_goal(coverage, fullpaths, description, status, srcloc):
    if not description:
        logging.debug("Found goal with no description")
        return coverage, fullpaths

    hit = parse_status(status)
    loc_path, loc_func, loc_line = srcloc
    desc_path, desc_func, desc_lines = parse_description(description)
    desc_path, desc_func, desc_lines = (desc_path or loc_path,
                                        desc_func or loc_func,
                                        desc_lines or [loc_line])

    # We expect (loc_path, loc_func) == (desc_path, desc_func) but loc_path
    # will be relative to root and desc_path will be either absolute or
    # relative to a working directory.  We want to use the loc_path
    # relative to root.
    # assert desc_func == loc_func

    # This expectation can be violated in several ways:
    # function versus function$link1 for inlined functions
    # Atomic_CompareAndSwap_u32 __atomic_compare_exchange_vU32 for intrinsics
    # So we will prefer the description name over the source location name
    if desc_func != loc_func:
        print("Using function name {} in place of {}".format(desc_func, loc_func))
        loc_func = desc_func

    fullpaths[desc_path] = loc_path

    for line in desc_lines:
        coverage = update_coverage(coverage, loc_path, loc_func, line, hit)
    return coverage, fullpaths

################################################################

def parse_xml_coverage(xmlfile, root=None):
    xml = parse.parse_xml_file(xmlfile)
    if xml is None:
        return {}, {}

    coverage = {}
    fullpaths = {}
    for goal in xml.iter("goal"):
        description = goal.get("description")
        if description is None:
            continue
        status = goal.get("status")
        loc = goal.find("location")
        srcloc = locationt.parse_xml_srcloc(loc, root=root)
        coverage, fullpaths = parse_goal(coverage, fullpaths,
                                         description, status, srcloc)
    return coverage, fullpaths

def parse_json_coverage(jsonfile, root=None):
    data = parse.parse_json_file(jsonfile)
    if data is None:
        return {}, {}

    goals = []
    for entry in data:
        if entry.get('goals'):
            goals = entry['goals']
            break

    coverage = {}
    fullpaths = {}
    for goal in goals:
        description = goal["description"]
        status = goal["status"]
        loc = goal["sourceLocation"]
        srcloc = locationt.parse_json_srcloc(loc, root=root)
        coverage, fullpaths = parse_goal(coverage, fullpaths,
                                         description, status, srcloc)
    return coverage, fullpaths

################################################################

def main():
    cover_xml = Coverage(xmlfile="coverage.xml", root="/Users/mrtuttle/freertos")
    print(json.dumps(cover_xml.coverage, indent=2, sort_keys=True))

    cover_json = Coverage(jsonfile="coverage.json", root="/Users/mrtuttle/freertos")
    print(json.dumps(cover_json.coverage, indent=2, sort_keys=True))
    print("equal = ", cover_xml == cover_json)

if __name__ == "__main__":
    main()
