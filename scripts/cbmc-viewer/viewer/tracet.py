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
import locationt

def binary_as_bytes(binary):
    if not binary:
        return binary
    bits = re.sub(r'\s', '', binary)
    bytes = re.findall('[01]{8}', bits)
    if bits != ''.join(bytes):
        return binary
    return ' '.join(bytes)

class Trace:
    def __init__(self,
                 traces=None, txtfile=None, xmlfile=None, jsonfile=None,
                 wkdir=None, root=None):
        """Load CBMC traces.

        Load traces from a json file, or parse the text or xml or
        json traces from CBMC.

        If a working directory is given, all relative paths are
        assumed relative to the working directory.  If a souce root is
        given, make all paths under this root relative paths relative
        to this root.
        """
        logging.debug("Trace: "
                      "traces=%s xmlfile=%s jsonfile=%s wkdir=%s root=%s",
                      traces, xmlfile, jsonfile, wkdir, root)

        data = traces or txtfile or jsonfile or xmlfile
        parser = (load_traces if traces else
                  parse_text_traces if txtfile else
                  parse_json_traces if jsonfile else
                  parse_xml_traces if xmlfile else None)

        if not data or not parser:
            print("No trace data found")
            logging.info("No trace data found")
            return
        self.traces = parser(data, root, wkdir)

    def dump(self):
        return json.dumps(self.traces, indent=2, sort_keys=True)

################################################################
# Load trace files: load, text, json, xml

def load_traces(loadfile):
    with open(loadfile) as data:
        return json.load(data)

################################################################

def parse_text_traces(textfile, root=None, wkdir=None):
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
            trace.append(parse_text_state(block, root, wkdir))
            continue
        if block.startswith('Assumption'):
            trace.append(parse_text_assumption(block, root, wkdir))
            continue
        if block.startswith('Violated property'):
            trace.append(parse_text_failure(block, root, wkdir))
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

def parse_text_state(block, root=None, wkdir=None):
    lines = block.splitlines()
    srcloc = locationt.parse_text_srcloc(
        lines[0], root=root, wkdir=wkdir, asdict=True
    )
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

def parse_text_assumption(block, root=None, wkdir=None):
    lines = block.splitlines()
    srcloc = locationt.parse_text_srcloc(
        lines[1], root=root, wkdir=wkdir, asdict=True
    )
    return {
        'kind': 'assumption',
        'location': srcloc,
        'detail': {
            'predicate': lines[2].strip()
        }
    }

def parse_text_failure(block, root=None, wkdir=None):
    lines = block.splitlines()
    srcloc = locationt.parse_text_srcloc(
        lines[1], root=root, wkdir=wkdir, asdict=True
    )
    return {
        'kind': 'failure',
        'location': srcloc,
        'detail': {
            'property': None,
            'reason': lines[2].strip()
        }
    }

################################################################

def parse_json_traces(jsonfile, root=None, wkdir=None):
    data = parse.parse_json_file(jsonfile)
    if data is None:
        return {}

    _ = wkdir # ignore

    results = [entry['result'] for entry in data if 'result' in entry][0]
    traces = {result['property']: parse_json_trace(result['trace'], root)
              for result in results if 'trace' in result}
    return traces

def parse_json_trace(steps, root=None):
    trace = [parse_json_step(step, root) for step in steps]
    return [step for step in trace if step is not None]

def parse_json_step(step, root=None):
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

    return parser(step, root)

def parse_json_failure(step, root=None):
    return {
        'kind': 'failure',
        'location': locationt.parse_json_srcloc(
            step.get('sourceLocation'), root, True
        ),
        'detail': {
            'property': step.get('property'),
            'reason': step.get('reason')
        }
    }

def parse_json_assignment(step, root=None):
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
        'location': locationt.parse_json_srcloc(
            step.get('sourceLocation'), root, True
        ),
        'detail': {
            'lhs': step['lhs'],
            'rhs-value': data or json.dumps(step['value']),
            'rhs-binary': binary_as_bytes(step['value'].get('binary'))
        }
    }

def parse_json_function_call(step, root=None):
    return {
        'kind': 'function-call',
        'location': locationt.parse_json_srcloc(
            step.get('sourceLocation'), root, True
        ),
        'detail': {
            'name': step['function']['displayName'],
            'location': locationt.parse_json_srcloc(
                step['function']['sourceLocation'], root, True
            )
        }
    }

def parse_json_function_return(step, root=None):
    return {
        'kind': 'function-return',
        'location': locationt.parse_json_srcloc(
            step.get('sourceLocation'), root, True
        ),
        'detail': {
            'name': step['function']['displayName'],
            'location': locationt.parse_json_srcloc(
                step['function']['sourceLocation'], root, True
            )
        }
    }

def parse_json_location_only(step, root=None):
    _ = step
    _ = root

################################################################

def parse_xml_traces(xmlfile, root=None, wkdir=None):
    xml = parse.parse_xml_file(xmlfile)
    if xml is None:
        return {}

    _ = wkdir # ignore

    traces = {}
    for line in xml.iter('result'):
        name, status = line.get('property'), line.get('status')
        if status == 'SUCCESS':
            continue
        traces[name] = parse_xml_trace(line.find('goto_trace'), root)

    return traces

def parse_xml_trace(steps, root=None):
    trace = [parse_xml_step(step, root) for step in steps]
    return [step for step in trace if step is not None]

def parse_xml_step(step, root=None):
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

    return parser(step, root)

def parse_xml_failure(step, root=None):
    return {
        'kind': 'failure',
        'location': locationt.parse_xml_srcloc(
            step.find('location'), root, True
        ),
        'detail': {
            'property': step.get('property'),
            'reason': step.get('reason')
        }
    }

def parse_xml_assignment(step, root=None):
    akind = step.get('assignment_type')
    kind = ('variable-assignment' if akind == 'state' else
            'parameter-assignment' if akind == 'actual_parameter' else None)
    if kind is None:
        raise UserWarning("Unknown xml assignment type: {}".format(akind))

    return {
        'kind': kind,
        'location': locationt.parse_xml_srcloc(
            step.find('location'), root, True
        ),
        'detail': {
            'lhs': step.find('full_lhs').text,
            'rhs-value': step.find('full_lhs_value').text,
            'rhs-binary': None
        }
    }

def parse_xml_function_call(step, root=None):
    return {
        'kind': 'function-call',
        'location': locationt.parse_xml_srcloc(
            step.find('location'), root, True
        ),
        'detail': {
            'name': step.find('function').get('display_name'),
            'location': locationt.parse_xml_srcloc(
                step.find('function').find('location'), root, True
            )
        }
    }

def parse_xml_function_return(step, root=None):
    return {
        'kind': 'function-return',
        'location': locationt.parse_xml_srcloc(
            step.find('location'), root, True
        ),
        'detail': {
            'name': step.find('function').get('display_name'),
            'location': locationt.parse_xml_srcloc(
                step.find('function').find('location'), root, True
            )
        }
    }

def parse_xml_location_only(step, root=None):
    _ = step
    _ = root

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
