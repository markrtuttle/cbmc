"""CBMC loop information"""

import json
import logging
import subprocess

import locationt
import parse
import runt

class Loop:
    """Manage CBMC loop information."""

    def __init__(self,
                 loops=None,
                 txtfile=None, xmlfile=None, jsonfile=None,
                 goto=None,
                 root=None):
        """Load CBMC loop information.

        Load the data from a json file, or parse the xml or json
        loop output from CBMC generated 'cbmc --show-loops'.
        If a souce root is given, make all paths under this root
        relative paths relative to this root.
        """
        logging.debug("Loops: loops=%s xmlfile=%s jsonfile=%s root=%s",
                      loops, xmlfile, jsonfile, root)

        if txtfile:
            raise UserWarning("Text files not allowed for loop data.")

        # coverage: loops -> (path, func, line)
        self.loops = {}

        if loops:
            with open(loops) as load:
                self.loops = json.load(load)['loops']
        elif jsonfile:
            self.loops = parse_json_loops(jsonfile, root)
        elif xmlfile:
            self.loops = parse_xml_loops(xmlfile, root)
        elif goto:
            self.loops = parse_goto_loops(goto, root)
        else:
            print("No loop information found")
            logging.info("No loop information found")

        # Loops in static functions FUNC may have names FUNC$link1.0
        # Replace the name FUNC$link1.0 with FUNC.0
        static_loops = [loop for loop in self.loops if '$link' in loop]
        for loop_name in static_loops:
            loop_data = self.loops[loop_name]
            loop_func, loop_index = loop_name.split('.')
            name = '{}.{}'.format(loop_func[:loop_func.find('$')],
                                  loop_index)
            del self.loops[loop_name]
            self.loops[name] = loop_data

    def names(self):
        return self.loops.keys()

    def lookup(self, name):
        return (self.loops.get(name, {}).get('file'),
                self.loops.get(name, {}).get('function'),
                self.loops.get(name, {}).get('line'))

    def dump(self):
        return json.dumps({'loops': self.loops}, indent=2)

def parse_json_data(data, root):
    loop_list = []
    for entry in data:
        if entry.get('loops'):
            loop_list = entry['loops']
            break

    loops = {}
    for loop in loop_list:
        name = loop['name']
        loc = loop['sourceLocation']
        loops[name] = locationt.parse_json_srcloc(loc, root=root, asdict=True)
    return loops

def parse_goto_loops(goto, root):
    cmd = ['cbmc', '--show-loops', '--json-ui', goto]
    try:
        result = runt.run(cmd)
        return parse_json_data(json.loads(result), root)
    except subprocess.CalledProcessError as err:
        logging.info('Failed to run %s: %s', cmd, str(err))
        return {}
    except json.decoder.JSONDecodeError as err:
        logging.info('Failed to parse output of %s: %s', cmd, str(err))
        return {}

def parse_json_loops(jsonfile, root):
    logging.debug("parse_json_loops: jsonfile=%s root=%s", jsonfile, root)

    data = parse.parse_json_file(jsonfile)
    if data is None:
        return {}

    return parse_json_data(data, root)

def parse_xml_loops(xmlfile, root):
    logging.debug("parse_xml_loops: xmlfile=%s root=%s", xmlfile, root)

    data = parse.parse_xml_file(xmlfile)
    if data is None:
        return {}

    loops = {}
    for loop in data.iter("loop"):
        name = loop.get("name")
        loc = loop.find("location")
        loops[name] = locationt.parse_xml_srcloc(loc, root=root, asdict=True)
    return loops
