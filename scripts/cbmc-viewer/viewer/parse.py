"""Parsing of xml and json files with limited error handling."""

from xml.etree import ElementTree
import json
import logging

def parse_xml_file(xfile):
    """Open and parse an xml file."""
    logging.debug("parse_xml_file: xfile=%s", xfile)

    try:
        with open(xfile) as data:
            return parse_xml_string(data.read(), xfile)
    except IOError as err:
        logging.debug("Can't open xml file %s: %s", xfile, err.strerror)
    return None

def parse_xml_string(xstr, xfile=None):
    """Parse an xml string."""
    logging.debug("parse_xml_string: xstr=%s xfile=%s", xstr[:100], xfile)

    try:
        # Messages printed by cbmc before the coverage data we care
        # about may quote from the code, and quoted null character
        # '\0' will appear as the string '&#0', which is unparsable by
        # ElementTree.
        xstr = xstr.replace('&#0;', 'null_char')
        return ElementTree.fromstring(xstr)
    except ElementTree.ParseError as err:
        logging.debug("Can't parse xml string %s...: %s", xstr[:40], str(err))
        if xfile:
            logging.debug("Can't parse xml file %s: %s", xfile, str(err))
    return None

def parse_json_file(jfile):
    """Open and parse an json file."""
    logging.debug("parse_json_file: jfile=%s", jfile)

    try:
        with open(jfile) as data:
            return parse_json_string(data.read(), jfile)
    except IOError as err:
        logging.debug("Can't open json file %s: %s", jfile, err.strerror)
    return None

def parse_json_string(jstr, jfile=None):
    """Parse an json string."""
    logging.debug("parse_json_string: jstr=%s jfile=%s", jstr[:100], jfile)

    try:
        return json.loads(jstr)
    except json.JSONDecodeError as err:
        string = jstr[:40]
        logging.debug("Can't parse json string %s...: %s", string, str(err))
        if jfile:
            logging.debug("Can't parse json file %s: %s", jfile, str(err))
    return None
