"""Extract traces from cbmc output.

Extract traces from cbmc output (both text and json) and summarize in
a manner consistent with the json representation of traces.  For now,
use the json representation and transform the text representation into
a skelleton of the json representation.
"""

import json
import re
import sys
import os
import logging

################################################################
# Important keys from an assignment step
#   {
#     "lhs": "additionalLength",
#     "sourceLocation": {
#       "file": "filename",
#       "function": "functionname",
#       "line": "integer",
#       "workingDirectory": "directoryname",
#     },
#     "stepType": "assignment",
#     "value": {
#       "binary": "00001101001101101000000000000010",
#       "data": "221675522u",
#       "name": "integer"
#     }
#   }
#
# Important keys from a property violation step
#   {
#     "property": "function.overflow.2",
#     "reason": "arithmetic overflow",
#     "sourceLocation": {
#       "file": "filename",
#       "function": "functionname",
#       "line": "integer",
#       "workingDirectory": "directoryname",
#     },
#     "stepType": "failure",
#   }

################################################################
# Extract traces from the json output of cbmc

def traces_from_json_results(results):
    traces = {}
    for result in results:
        if result.get('status') == 'FAILURE':
            name, trace = result['property'], result['trace']
            traces[name] = trace
    return traces

def traces_from_json_output(logname, blddir, srcdir):
    with open(logname) as loghandle:
        log = json.load(loghandle)

    for entry in log:
        if entry.get('result'):
            traces = traces_from_json_results(entry['result'])
            return cleanup_srcloc_in_traces(traces, blddir, srcdir)
    return None

################################################################
# Extract traces from the text output of cbmc
#
# There is no reason to use text output from cbmc, except that it is
# easier for the user to read to monitor progress while the property
# checking is going on, and for cbmc-viewer legacy reasons.

def parse_srcloc(srcloc):
    match = re.search(r'file ([\w./\\<>-]+) function (\w+) line (\d+)',
                      srcloc.strip())
    if match:
        return {"file": match.group(1),
                "function": match.group(2),
                "line": match.group(3),
                "workingDirectory": "."}
    return None

def parse_assignment(assignment):
    lhs, rhs = assignment.strip().split('=', 1)
    binary = None
    match = re.match(r'(.*) \(([{}\[\],01 ]+)\)$', rhs)
    if match:
        rhs = match.group(1)
        binary = match.group(2)
    return (lhs,
            {"binary": binary,
             "data": rhs,
             "name": None,
             }
            )

def parse_step(srcloc, assignment):
    loc = parse_srcloc(srcloc)
    lhs, value = parse_assignment(assignment)
    return {"lhs": lhs,
            "sourceLocation": loc,
            "stepType": "assignment",
            "value": value}

def parse_violation(srcloc, description):
    loc = parse_srcloc(srcloc)
    return {"property": None,
            "reason": description,
            "sourceLocation": loc,
            "stepType": "failure"}

def trace_from_text(text):
    trace = []
    lines = text.splitlines()
    next_line = lambda: lines.pop(0).strip()
    while lines:
        line = next_line()
        if not line:
            continue
        if line.startswith('State'):
            srcloc = line
            # skip separator (horizontal line of dashes)
            _ = next_line()
            # assignment may be broken over several lines
            # (for example, big structs or arrays)
            assignment_lines = []
            nextline = next_line()
            while nextline:
                assignment_lines.append(nextline)
                nextline = next_line()
            assignment = ' '.join(assignment_lines)
            trace.append(parse_step(srcloc, assignment))
            continue
        if line.startswith('Violated property'):
            srcloc = next_line()
            description = next_line()
            # skip: json traces do not include the expression being checked
            _ = next_line()
            trace.append(parse_violation(srcloc, description))
            continue
        if line.startswith('Assumption'):
            # skip: json traces do not include assumptions
            _ = next_line()
            _ = next_line()
            continue
        if line.startswith('**'):
            # skip: final summary line
            continue
        if line.startswith('VERIFICATION'):
            # skip: final summary line
            continue
        sys.stderr.write('\nUnexpected line in trace: {}\n\n'.format(line))
        logging.info('\nUnexpected line in trace: %s\n\n', line)
    return trace

def traces_from_text_output(logname, blddir, srcdir):
    trace_texts = {}
    with open(logname) as log:
        name = ""
        trace = ""
        for line in log:
            match = re.match('^Trace for (.*):', line)
            if match:
                if name:
                    trace_texts[name] = trace
                name = match.group(1)
                trace = ""
                continue
            if name:
                trace += line
        if name:
            trace_texts[name] = trace

    traces = {}
    for name, text in trace_texts.items():
        traces[name] = trace_from_text(text)

    return cleanup_srcloc_in_traces(traces, blddir, srcdir)

################################################################

def cleanup_srcloc(srcloc, blddir, srcdir):
    filename = srcloc.get('file')
    wd = srcloc.get('workingDirectory')

    # skip source locations for cbmc built-in functions
    if filename.startswith('<') and filename.endswith('>'):
        return srcloc

    # generate absolute paths to all source files
    paths = []
    if blddir:
        paths.append(blddir)
    if wd:
        paths.append(wd)
    paths.append(filename)
    filename = os.path.abspath(os.path.join(*paths))

    # generate relative paths to source files under srcdir
    if srcdir:
        # goto-cc may have resolved symbolic links in srcloc
        # srcdir may be specified with unresolved symbolic links
        realsrc = os.path.realpath(srcdir)
        realfile = os.path.realpath(filename)
        if realfile.startswith(realsrc):
            filename = realfile[len(realsrc):].lstrip(os.sep)
            wd = srcdir

    srcloc['file'] = filename
    srcloc['workingDirectory'] = wd
    return srcloc

def cleanup_srcloc_in_step(step, blddir, srcdir):
    srcloc = step.get('sourceLocation')
    if srcloc:
        srcloc = cleanup_srcloc(srcloc, blddir, srcdir)
    step['sourceLocation'] = srcloc
    return step

def cleanup_srcloc_in_trace(trace, blddir, srcdir):
    return [cleanup_srcloc_in_step(step, blddir, srcdir)
            for step in trace]

def cleanup_srcloc_in_traces(traces, blddir, srcdir):
    return {name: cleanup_srcloc_in_trace(trace, blddir, srcdir)
            for name, trace in traces.items()}

################################################################

def traces_from_cbmc(log, blddir=None, srcdir=None, txt=False, jsn=False):
    if jsn:
        return traces_from_json_output(log, blddir, srcdir)
    if txt:
        return traces_from_text_output(log, blddir, srcdir)
    if log.endswith('.json'):
        return traces_from_json_output(log, blddir, srcdir)
    if log.endswith('.txt'):
        return traces_from_text_output(log, blddir, srcdir)
    return traces_from_json_output(log, blddir, srcdir)

################################################################
