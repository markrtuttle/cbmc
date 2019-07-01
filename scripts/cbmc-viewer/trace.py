"""The error traces from CBMC."""
from __future__ import print_function

from builtins import object
import os
import re
import sys


class Trace(object):
    """Parse, markup, and manage error traces."""

    def __init__(self, markup):
        """Initialize error traces."""
        self.trace = {}
        self.markup = markup

    def lookup(self, error):
        """Look up trace by error name."""
        return self.trace.get(error, None)

    def link_trace(self, error, text=""):
        """Link to a trace by error name."""
        text = text or error

        trace = self.lookup(error)
        if not trace:
            return text

        return '<a href="traces/{}.html">{}</a>'.format(error, text)

    def markup_trace(self, trace):
        """Annotate a trace."""
        lines = []
        for line in trace.split('\n'):
            lines.append(self.markup.markup_source_location(line,
                                                            depth=1,
                                                            target="code"))
        return "\n".join(lines)

    def generate_trace(self, error, htmldir="", htmlfile="", properties=None):
        """Generate an annotated trace file."""
        trace = self.lookup(error)
        if not trace:
            return

        filedir = htmldir or 'html'
        filedir = "{}/traces".format(filedir)
        filename = htmlfile or '{}.html'.format(error)
        filepath = '{}/{}'.format(filedir, filename)

        try:
            os.makedirs(filedir)
        except OSError:
            if not os.path.isdir(filedir):
                raise

        try:
            fp = open(filepath, "w")
        except IOError as e:
            print("Unable to open {} for writing: {}" \
                .format(filepath, e.strerror))
            sys.exit()

        html = []
        html.append('<html><head><title>{}</title></head><body><h1>{}</h1>'
                    .format(error, error))
        html.append('Trace for {}:'
                    .format(self.markup_error_description(error, properties)))
        html.append('<pre>')
        html.append(self.markup_trace(trace))
        html.append('</pre>')
        html.append('</body></html>')

        fp.write("\n".join(html))
        fp.close()

    def generate_traces(self, htmldir=None, htmlfile=None, properties=None):
        """Generate all annotated trace files."""
        for error in self.trace:
            self.generate_trace(error, htmldir=htmldir, htmlfile=htmlfile,
                                properties=properties)

    @staticmethod
    def markup_error(error, properties=None):
        """Link an error name to an annotated source code line."""
        if not (properties and properties.property.get(error, None)):
            return error
        srcfile = properties.property[error]["file"]
        line = properties.property[error]["line"]
        return '<a href="../{}.html#{}">{}</a>'.format(srcfile, line, error)

    @staticmethod
    def markup_error_description(error, properties=None):
        """Link an error description to an annotated source code line."""
        if not (properties and properties.property.get(error, None)):
            return error
        srcfile = properties.property[error]["file"]
        line = properties.property[error]["line"]
        return ('<a href="../{}.html#{}">{}</a> at line {} in file {}'
                .format(srcfile, line, error, line, srcfile))


class TraceCBMC(Trace):
    """Parse, markup, and manage error traces produced by 'cbmc --trace'."""

    def __init__(self, log, markup, srcloc):
        """Initialize error traces from cbmc output."""
        super(TraceCBMC, self).__init__(markup)

        if not log:
            return

        try:
            fp = open(log, "r")
        except IOError as e:
            print (("Can't read cbmc traces: "
                    "Unable to open {} for reading: {}")
                   .format(log, e.strerror))
            return

        name = ""
        trace = ""
        for line in fp:
            match = re.match('^Trace for (.*):', line)
            if match:
                if name:
                    self.trace[name] = trace
                name = match.group(1)
                trace = ""
                continue
            if name:
                trace += srcloc.clean_source_location(line)
        if name:
            self.trace[name] = trace

        self.markup = markup


class TraceStorm(Trace):
    """Parse, markup, and manage error traces produced by cbmc-storm."""

    def __init__(self, storm, markup):
        """Initialize error traces from cbmc-storm output."""
        super(TraceStorm, self).__init__(markup)

        for name in storm.property:
            self.trace[name] = storm.property[name]['trace']