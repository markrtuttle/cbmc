# pylint: disable=missing-docstring

#select hidden=false
#
#each step has location, kind, detail
#
#kind
#  assumption
#  failure
#  variable-assignment
#  parameter-assignment
#     lhs
#     rhs-value
#     rhs-binary
#
#  function-call
#  function-return
#  location-only

import re
import logging
import json

import parse

def binary_as_bytes(binary):
    if not binary:
        return binary
    bits = re.sub(r'\s', '', binary)
    bites = re.findall('[01]{8}', bits)
    if bits != ''.join(bites):
        return binary
    return ' '.join(bites)

class Trace:
    def __init__(self,
                 traces=None, txtfile=None, xmlfile=None, jsonfile=None,
                 location=None):
        """Load CBMC traces.

        Load traces from a json file, or parse the text or xml or
        json traces from CBMC.

        If a working directory is given, all relative paths are
        assumed relative to the working directory.  If a souce root is
        given, make all paths under this root relative paths relative
        to this root.
        """
        logging.debug("Trace: "
                      "traces=%s xmlfile=%s jsonfile=%s",
                      traces, xmlfile, jsonfile)

        data = traces or txtfile or jsonfile or xmlfile
        parser = (load_traces if traces else
                  parse_text_traces if txtfile else
                  parse_json_traces if jsonfile else
                  parse_xml_traces if xmlfile else None)

        if not data or not parser:
            print("No trace data found")
            logging.info("No trace data found")
            return
        self.traces = parser(data, location)

    def dump(self):
        return json.dumps(self.traces, indent=2, sort_keys=True)

################################################################
# Load trace files: load, text, json, xml

def load_traces(loadfile):
    with open(loadfile) as data:
        return json.load(data)

################################################################

def parse_text_traces(textfile, location):
    with open(textfile) as data:
        lines = '\n'.join(data.read().splitlines())
        blocks = re.split(r'\n\n+', lines)

    traces = {}

    name = None
    trace = []
    in_trace = False
    for block in blocks:
        if block.startswith('Trace for'):
            if name:
                traces[name] = trace
                name = None
                trace = []
            name = block.split()[-1][:-1]
            in_trace = True
            continue
        if not in_trace:
            continue
        if block.startswith('State'):
            trace.append(parse_text_state(block, location))
            continue
        if block.startswith('Assumption'):
            trace.append(parse_text_assumption(block, location))
            continue
        if block.startswith('Violated property'):
            trace.append(parse_text_failure(block, location))
            continue
        if block.startswith('** '):
            if name:
                traces[name] = trace
            break
        raise UserWarning("Unknown block: {}".format(block))

    return traces

def parse_text_assignment(string):
    # trailing binary expression (exp) may be integer, struct, or unknown ?
    match = re.match(r'([^=]+)=(.+) \(([?{},01 ]+)\)', string.strip())
    if match:
        return list(match.groups()[:3])
    match = re.match('([^=]+)=(.+)', string.strip())
    if match:
        return list(match.groups()[:2]) + [None]
    raise UserWarning("Can't parse assignment: {}".format(string))

def parse_text_state(block, location):
    lines = block.splitlines()
    srcloc = location.parse_text_srcloc(lines[0], asdict=True)
    # assignment may be split over remaining lines in block
    lhs, rhs_value, rhs_binary = parse_text_assignment(' '.join(lines[2:]))
    return {
        'kind': 'variable-assignment',
        'location': srcloc,
        'detail': {
            'lhs': lhs,
            'rhs-value': rhs_value,
            'rhs-binary': rhs_binary
        }
    }

def parse_text_assumption(block, location):
    lines = block.splitlines()
    srcloc = location.parse_text_srcloc(lines[1], asdict=True)
    return {
        'kind': 'assumption',
        'location': srcloc,
        'detail': {
            'predicate': lines[2].strip()
        }
    }

def parse_text_failure(block, location):
    lines = block.splitlines()
    srcloc = location.parse_text_srcloc(lines[1], asdict=True)
    return {
        'kind': 'failure',
        'location': srcloc,
        'detail': {
            'property': None,
            'reason': lines[2].strip()
        }
    }

################################################################

def parse_json_traces(jsonfile, location):
    data = parse.parse_json_file(jsonfile)
    if data is None:
        return {}

    results = [entry['result'] for entry in data if 'result' in entry][0]
    traces = {result['property']: parse_json_trace(result['trace'], location)
              for result in results if 'trace' in result}
    return traces

def parse_json_trace(steps, location):
    trace = [parse_json_step(step, location) for step in steps]
    return [step for step in trace if step is not None]

def parse_json_step(step, location):
    if step.get('hidden'):
        return None

    kind = step['stepType']
    parser = (parse_json_failure if kind == 'failure' else
              parse_json_assignment if kind == 'assignment' else
              parse_json_function_call if kind == 'function-call' else
              parse_json_function_return if kind == 'function-return' else
              parse_json_location_only if kind == 'location-only' else None)
    if parser is None:
        raise UserWarning("Unknown json step type: {}".format(kind))

    return parser(step, location)

def parse_json_failure(step, location):
    return {
        'kind': 'failure',
        'location': location.parse_json_srcloc(step.get('sourceLocation'), True),
        'detail': {
            'property': step.get('property'),
            'reason': step.get('reason')
        }
    }

def parse_json_assignment(step, location):
    akind = step.get('assignmentType')
    kind = ('variable-assignment' if akind == 'variable' else
            'parameter-assignment' if akind == 'actual-parameter' else None)
    if kind is None:
        raise UserWarning("Unknown json assignment type: {}".format(akind))

    # &v is represented as {name: pointer, data: v}
    # NULL is represented as {name: pointer, data:{(basetype *)NULL)}
    data = step['value'].get('data')
    if step['value'].get('name') == 'pointer' and data and 'NULL' not in data:
        data = '&{}'.format(data)

    return {
        'kind': kind,
        'location': location.parse_json_srcloc(step.get('sourceLocation'), True),
        'detail': {
            'lhs': step['lhs'],
            'rhs-value': data or json.dumps(step['value']),
            'rhs-binary': binary_as_bytes(step['value'].get('binary'))
        }
    }

def parse_json_function_call(step, location):
    return {
        'kind': 'function-call',
        'location': location.parse_json_srcloc(
            step.get('sourceLocation'),
            True
        ),
        'detail': {
            'name': step['function']['displayName'],
            'location': location.parse_json_srcloc(
                step['function']['sourceLocation'],
                True
            )
        }
    }

def parse_json_function_return(step, location):
    return {
        'kind': 'function-return',
        'location': location.parse_json_srcloc(
            step.get('sourceLocation'),
            True
        ),
        'detail': {
            'name': step['function']['displayName'],
            'location': location.parse_json_srcloc(
                step['function']['sourceLocation'],
                True
            )
        }
    }

def parse_json_location_only(step, location):
    _ = step
    _ = location

################################################################

def parse_xml_traces(xmlfile, location):
    xml = parse.parse_xml_file(xmlfile)
    if xml is None:
        return {}

    traces = {}
    for line in xml.iter('result'):
        name, status = line.get('property'), line.get('status')
        if status == 'SUCCESS':
            continue
        traces[name] = parse_xml_trace(line.find('goto_trace'), location)

    return traces

def parse_xml_trace(steps, location):
    trace = [parse_xml_step(step, location) for step in steps]
    return [step for step in trace if step is not None]

def parse_xml_step(step, location):
    if step.get('hidden') == 'true':
        return None

    kind = step.tag
    parser = (parse_xml_failure if kind == 'failure' else
              parse_xml_assignment if kind == 'assignment' else
              parse_xml_function_call if kind == 'function_call' else
              parse_xml_function_return if kind == 'function_return' else
              parse_xml_location_only if kind == 'location-only' else None)

    if parser is None:
        raise UserWarning("Unknown xml step type: {}".format(kind))

    return parser(step, location)

def parse_xml_failure(step, location):
    return {
        'kind': 'failure',
        'location': location.parse_xml_srcloc(
            step.find('location'),
            True
        ),
        'detail': {
            'property': step.get('property'),
            'reason': step.get('reason')
        }
    }

def parse_xml_assignment(step, location):
    akind = step.get('assignment_type')
    kind = ('variable-assignment' if akind == 'state' else
            'parameter-assignment' if akind == 'actual_parameter' else None)
    if kind is None:
        raise UserWarning("Unknown xml assignment type: {}".format(akind))

    return {
        'kind': kind,
        'location': location.parse_xml_srcloc(
            step.find('location'),
            True
        ),
        'detail': {
            'lhs': step.find('full_lhs').text,
            'rhs-value': step.find('full_lhs_value').text,
            'rhs-binary': None
        }
    }

def parse_xml_function_call(step, location):
    return {
        'kind': 'function-call',
        'location': location.parse_xml_srcloc(
            step.find('location'),
            True
        ),
        'detail': {
            'name': step.find('function').get('display_name'),
            'location': location.parse_xml_srcloc(
                step.find('function').find('location'),
                True
            )
        }
    }

def parse_xml_function_return(step, location):
    return {
        'kind': 'function-return',
        'location': location.parse_xml_srcloc(
            step.find('location'),
            True
        ),
        'detail': {
            'name': step.find('function').get('display_name'),
            'location': location.parse_xml_srcloc(
                step.find('function').find('location'),
                True
            )
        }
    }

def parse_xml_location_only(step, location):
    _ = step
    _ = location

#step type
#
#choose hidden=false
#
#kind
#assumption
#violation
#
#        "stepType": "assignment",
#            "assignmentType": "actual-parameter",
#            "assignmentType": "variable",
#
#            "stepType": "failure",
#            "stepType": "function-call",
#            "stepType": "function-return",
#            "stepType": "location-only",
#
#
#
#
#        <assignment assignment_type="state"
#    <assignment assignment_type="actual_parameter"
#    <failure hidden="false" property="strncmp.unwind.0"
#       reason="unwinding assertion loop 0"
#       step_nr="1420" thread="0">
#
#    <function_call
#            <function_return
#
#
