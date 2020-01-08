"""CBMC loop information"""

import json
import logging
import subprocess

import parse
import runt

class Loop:
    """Manage CBMC loop information."""

    def __init__(self,
                 loops=None,
                 txtfile=None, xmlfile=None, jsonfile=None,
                 goto=None,
                 location=None):
        """Load CBMC loop information.

        Load the data from a json file, or parse the xml or json
        loop output from CBMC generated 'cbmc --show-loops'.
        If a souce root is given, make all paths under this root
        relative paths relative to this root.
        """
        logging.debug("Loops: loops=%s xmlfile=%s jsonfile=%s",
                      loops, xmlfile, jsonfile)

        if txtfile:
            raise UserWarning("Text files not allowed for loop data.")

        # coverage: loops -> (path, func, line)
        self.loops = {}

        if loops:
            with open(loops) as load:
                self.loops = json.load(load)['loops']
        elif jsonfile:
            self.loops = parse_json_loops(jsonfile, location)
        elif xmlfile:
            self.loops = parse_xml_loops(xmlfile, location)
        elif goto:
            self.loops = parse_goto_loops(goto, location)
        else:
            print("No loop information found")
            logging.info("No loop information found")

    def dump(self):
        return json.dumps({'loops': self.loops}, indent=2)


def parse_json_data(data, location):
    loop_list = []
    for entry in data:
        if entry.get('loops'):
            loop_list = entry['loops']
            break

    loops = {}
    for loop in loop_list:
        name = loop['name']
        loc = loop['sourceLocation']
        loops[name] = location.parse_json_srcloc(loc, asdict=True)
    return loops

def parse_goto_loops(goto, location):
    cmd = ['cbmc', '--show-loops', '--json-ui', goto]
    try:
        result = runt.run(cmd)
        return parse_json_data(json.loads(result), location)
    except subprocess.CalledProcessError as err:
        logging.info('Failed to run %s: %s', cmd, str(err))
        return {}
    except json.decoder.JSONDecodeError as err:
        logging.info('Failed to parse output of %s: %s', cmd, str(err))
        return {}

def parse_json_loops(jsonfile, location):
    logging.debug("parse_json_loops: jsonfile=%s", jsonfile)

    data = parse.parse_json_file(jsonfile)
    if data is None:
        return {}

    return parse_json_data(data, location)

def parse_xml_loops(xmlfile, location):
    logging.debug("parse_xml_loops: xmlfile=%s", xmlfile)

    data = parse.parse_xml_file(xmlfile)
    if data is None:
        return {}

    loops = {}
    for loop in data.iter("loop"):
        name = loop.get("name")
        loc = loop.find("location")
        loops[name] = location.parse_xml_srcloc(loc, asdict=True)
    return loops
