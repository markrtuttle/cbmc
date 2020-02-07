#!/usr/bin/env python3

#pylint: disable=missing-docstring

import re
import json
import logging

import parse

################################################################

TEXT_PROGRAM = 'program'
TEXT_MESSAGE_TEXT = 'messageText'
TEXT_MESSAGE_TYPE = 'messageType'
TEXT_STATUS_MESSAGE = 'STATUS-MESSAGE'
TEXT_WARNING_MESSAGE = 'WARNING'
TEXT_RESULT = 'result'
TEXT_PROVER_STATUS = 'cProverStatus'

JSON_PROGRAM = 'program'
JSON_MESSAGE_TEXT = 'messageText'
JSON_MESSAGE_TYPE = 'messageType'
JSON_STATUS_MESSAGE = 'STATUS-MESSAGE'
JSON_WARNING_MESSAGE = 'WARNING'
JSON_RESULT = 'result'
JSON_PROVER_STATUS = 'cProverStatus'

PROGRAM = 'program'
STATUS = 'status'
WARNING = 'warning'
RESULT = 'result'
PROVER = 'prover-status'

################################################################

class Result:
    def __init__(self,
                 results=None, txtfile=None, xmlfile=None, jsonfile=None,
                 wkdir=None, root=None):
        """Load CBMC results.

        Load results from a json file, or parse the text or xml or
        json results from CBMC.

        If a working directory is given, all relative paths are
        assumed relative to the working directory.  If a souce root is
        given, make all paths under this root relative paths relative
        to this root.
        """
        logging.debug("Result: "
                      "results=%s xmlfile=%s jsonfile=%s wkdir=%s root=%s",
                      results, xmlfile, jsonfile, wkdir, root)

        self.program = None
        self.status = []
        self.warning = []
        self.results = {True: {}, False: {}}
        self.prover = None

        data = results or txtfile or jsonfile or xmlfile
        parser = (load_results if results else
                  parse_text_results if txtfile else
                  parse_json_results if jsonfile else
                  parse_xml_results if xmlfile else None)

        if not data or not parser:
            print("No results data found")
            logging.info("No results data found")
            return
        results = parser(data)

        self.program = results[PROGRAM]
        self.status = results[STATUS]
        self.warning = results[WARNING]
        self.results = {key: sorted(val)
                        for key, val in results[RESULT].items()}
        self.prover = results[PROVER]

    def dump(self):
        return json.dumps(
            {
                PROGRAM: self.program,
                STATUS: self.status,
                WARNING: self.warning,
                RESULT: self.results,
                PROVER: self.prover
            },
            indent=2)

################################################################
# Load result files: load, text, json, xml

def load_results(loadfile):
    with open(loadfile) as data:
        return json.load(data)

def parse_text_results(textfile):
    results = {
        PROGRAM: None, STATUS: [], WARNING: [],
        RESULT: {True: {}, False: {}}, PROVER: None
    }

    section = 'none'
    with open(textfile) as data:
        for line in data:
            line = line.strip()
            if not line:
                continue
            if line.startswith('CBMC version'):
                results[STATUS].append(line)
                results[PROGRAM] = line
                continue
            if line.startswith('**** WARNING:'):
                results[WARNING].append(line)
                continue
            if line == 'VERIFICATION FAILED':
                results[STATUS].append(line)
                results[PROVER] = 'failure'
                continue
            if line == 'VERIFICATION SUCCEEDED':
                results[STATUS].append(line)
                results[PROVER] = 'success'
                continue
            if line.startswith('** Results:'):
                section = 'result'
                continue
            if line.startswith('Trace for '):
                section = 'trace'
                # trace module collects traces
                continue
            if section == 'result':
                match = re.match(
                    r'\[(.*)\] line [0-9]+ (.*): ((FAILURE)|(SUCCESS))',
                    line)
                if match:
                    name, desc, status = match.groups()[:3]
                    if status == 'SUCCESS':
                        results[RESULT][True][name] = desc
                    else:
                        results[RESULT][False][name] = desc
                continue
            if section == 'trace':
                # trace module collects traces
                continue
            else:
                results[STATUS].append(line)

    return results

def parse_json_results(jsonfile):
    data = parse.parse_json_file(jsonfile)
    if data is None:
        return {}

    results = {
        PROGRAM: None, STATUS: [], WARNING: [],
        RESULT: {True: {}, False: {}}, PROVER: None
    }

    for entry in data:
        if 'program' in entry:
            results[PROGRAM] = entry['program']
            continue

        if "messageType" in entry:
            kind = entry['messageType']
            text = entry['messageText']
            if kind == 'STATUS-MESSAGE':
                results[STATUS].append(text)
                continue
            if kind == 'WARNING':
                results[WARNING].append(text)
                continue
            raise UserWarning('Unknown CBMC json message type {}'.format(kind))

        if "result" in entry:
            for res in entry['result']:
                name, desc, status = (
                    res['property'], res['description'], res['status']
                )
                if status == 'SUCCESS':
                    results[RESULT][True][name] = desc
                else:
                    results[RESULT][False][name] = desc
            continue

        if 'cProverStatus' in entry:
            results[PROVER] = entry['cProverStatus']
            continue

    return results

def parse_xml_results(xmlfile):
    xml = parse.parse_xml_file(xmlfile)
    if xml is None:
        return {}

    results = {
        PROGRAM: None, STATUS: [], WARNING: [],
        RESULT: {True: {}, False: {}}, PROVER: None
    }

    line = xml.find('program')
    if line is not None: # Why does "if line:" not work?
        results[PROGRAM] = line.text

    for line in xml.iter('message'):
        kind = line.get('type')
        if kind == 'STATUS-MESSAGE':
            results[STATUS].append(line.find('text').text)
            continue
        if kind == 'WARNING':
            results[WARNING].append(line.find('text').text)
            continue

    if xml.find('result'):
        # cbmc produced all results as usual
        for line in xml.iter('result'):
            name, desc, status = line.get('property'), None, line.get('status')
            if status == 'SUCCESS':
                results[RESULT][True][name] = desc
            else:
                results[RESULT][False][name] = desc
    elif xml.find('goto_trace'):
        # cbmc produced only a one one after being run with --stop-on-fail
        failure = xml.find('goto_trace').find('failure')
        name, desc = failure.get('property'), failure.get('reason')
        results[RESULT][False][name] = desc

    line = xml.find('cprover-status')
    if line is not None: # Why does "if line:" not work?
        results[PROVER] = line.text.lower()

    return results

################################################################
# What follows is some old code used to scan the results

################################################################
# Loop unwinding statistics

def extract_loop_statistics(status):
    return [line for line in status
            if line.startswith('Not unwinding loop')]

def unwound_loops(cbmc):
    loops = []
    for line in cbmc[STATUS]:
        match = re.match('Not unwinding loop (.*) iteration .* '
                         'file (.*) line (.*) function (.*) thread (.*)',
                         line)
        if match:
            loops.append({'loop': match.group(1),
                          'file': match.group(2),
                          'line': match.group(3),
                          'function': match.group(4)})
    return loops

################################################################
# SAT statistics

def format_sat_invocations(header, variables, clauses, result, runtime):
    assert len(header) == len(variables)
    assert len(header) == len(clauses)
    assert len(header) == len(result)
    assert len(header) == len(runtime)

    summary = []
    for var, cls, res, rtm in zip(variables, clauses, result, runtime):
        summary.append({'variables': var,
                        'clauses': cls,
                        'result': res,
                        'runtime': rtm})
    return summary

def sat_invocations(cbmc):
    size = None
    vcc = None
    header = []
    variables = []
    clauses = []
    result = []
    runtime = []

    for line in cbmc[STATUS]:
        match = re.match('size of program expression: ([0-9]+) steps', line)
        if match:
            size = int(match.group(1))
            continue

        match = re.match(r'Generated ([0-9]+) VCC\(s\), '
                         r'([0-9]+) remaining after simplification', line)
        if match:
            vcc = int(match.group(2))
            continue

        if line == 'Solving with MiniSAT 2.2.1 with simplifier':
            header.append(line)
            continue

        match = re.match('([0-9]+) variables, ([0-9]+) clauses', line)
        if match:
            variables.append(int(match.group(1)))
            clauses.append(int(match.group(2)))
            continue

        match = re.match('SAT checker: instance is ([A-Z]+)', line)
        if match:
            result.append(match.group(1))
            continue

        match = re.match('Runtime decision procedure: ([0-9.]+.*)', line)
        if match:
            runtime.append(match.group(1))
            continue

    return {'steps': size,
            'vccs': vcc,
            'invocations': format_sat_invocations(header, variables,
                                                  clauses, result, runtime)}

################################################################
# Traces

def value_to_string(value, depth=10, length=10):
    if value.get('data'):
        return value['data']

    if value.get('members'):
        members = ['.{}: {}'
                   .format(mbr['name'],
                           value_to_string(mbr['value'], depth-1, length))
                   for mbr in value['members']][:length]
        return '{' + ', '.join(members) + '}'

    if value.get('elements'):
        elements = [value_to_string(elt['value'], depth-1, length) for
                    elt in value['elements']][:length]
        return '[' + ', '.join(elements) + ']'

    print('Unknown value:', json.dumps(value))
    return json.dumps(value)

def format_step(step):
    if not step.get('value'):
        return step
    step['value'] = value_to_string(step['value'])
    return step

def traces(cbmc):
    return {result['property']: [format_step(step) for step in result['trace']]
            for result in cbmc[RESULT]
            if result['status'] == 'FAILURE'}

################################################################
