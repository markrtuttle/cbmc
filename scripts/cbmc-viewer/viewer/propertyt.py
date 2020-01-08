#pylint: disable=missing-docstring

"""CBMC property information"""

import json
import logging

import parse

class Property:
    """Manage CBMC property information."""

    def __init__(self, properties=None,
                 txtfile=None, xmlfile=None, jsonfile=None,
                 location=None):
        """Load CBMC property information.

        Load the data from a json file, or parse the xml or json
        property output from CBMC generated 'cbmc --show-properties'.
        If a souce root is given, make all paths under this root
        relative paths relative to this root.
        """
        logging.debug("Properties: properties=%s xmlfile=%s jsonfile=%s",
                      properties, xmlfile, jsonfile)

        if txtfile:
            raise UserWarning("Text files not allowed for property data.")

        # properties: name -> (class, description, expression, location)
        self.properties = {}

        if properties:
            with open(properties) as load:
                self.properties = json.load(load)['properties']
        elif jsonfile:
            self.properties = parse_json_properties(jsonfile, location)
        elif xmlfile:
            self.properties = parse_xml_properties(xmlfile, location)
        else:
            print("No property information found")
            logging.info("No property information found")

    def dump(self):
        return json.dumps({'properties': self.properties}, indent=2)

def parse_json_properties(jsonfile, location):
    logging.debug("parse_json_properties: jsonfile=%s", jsonfile)

    data = parse.parse_json_file(jsonfile)
    if data is None:
        return {}

    property_list = []
    for entry in data:
        if entry.get('properties'):
            property_list = entry['properties']
            break

    properties = {}
    for prop in property_list:
        name = prop['name']
        klass = prop['class']
        description = prop['description']
        expression = prop['expression']
        loc = prop['sourceLocation']
        properties[name] = {
            'class': klass,
            'description': description,
            'expression': expression,
            'location': location.parse_json_srcloc(loc, asdict=True)
        }
    return properties


def parse_xml_properties(xmlfile, location):
    logging.debug("parse_xml_properties: xmlfile=%s", xmlfile)

    data = parse.parse_xml_file(xmlfile)
    if data is None:
        return {}

    properties = {}
    for prop in data.iter("property"):
        name = prop.get("name")
        klass = prop.get("class")
        description = prop.find("description").text
        expression = prop.find("expression").text
        loc = prop.find("location")
        properties[name] = {
            'class': klass,
            'description': description,
            'expression': expression,
            'location': location.parse_xml_srcloc(loc, asdict=True)
        }
    return properties
