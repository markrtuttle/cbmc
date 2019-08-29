"""The error traces from CBMC."""

import os
import logging
import json
import html

import make_traces

class Trace:
    """Parse, markup, and manage error traces."""

    ################################################################
    # Public methods of the trace class

    def __init__(self, results=None, traces=None, srcdir=None, blddir=None):
        """Initialize error traces from cbmc output."""
        self.trace = {}

        if not results and not traces:
            msg = ('Skipping trace generation: '
                   'No cbmc output or cbmc trace file specified.')
            print(msg)
            logging.info(msg)

        if traces:
            with open(traces) as handle:
                self.trace = json.load(handle)
            return

        if results:
            self.trace = make_traces.traces_from_cbmc(results, blddir, srcdir)
            return

    def link_trace(self, error, text=""):
        """Link to an annotated trace specified by the name of the error."""
        text = text or error

        trace = self.trace.get(error)
        if not trace:
            return text

        return '<a href="traces/{}.html">{}</a>'.format(error, text)

    def generate_traces(self, htmldir=None):
        """Generate annotated traces."""
        for error in self.trace:
            self.generate_trace(error, self.trace[error], htmldir=htmldir)

    ################################################################
    # Private methods of the trace class

    @staticmethod
    def annotate_srcloc(srcloc, top='..'):
        if not srcloc:
            return None

        filename = srcloc.get('file')
        function = srcloc.get('function')
        line = srcloc.get('line')

        internal = lambda str: str.startswith('<') and str.endswith('>')
        link = 'source'
        if filename and line and not internal(filename):
            link = '<a href="{}/{}.html#{}">source</a>'.format(
                top, filename, line)

        span = '[{}] File {} Function {} Line {}'.format(
            link, html.escape(filename, quote=False),
            html.escape(function, quote=False), line)
        return '<span class="srcloc">{}</span>'.format(span)

    def annotate_assignment(self, step):
        srcloc = step.get('sourceLocation')
        lhs = step['lhs']
        rhs = step['value'].get('data') or step['value'].get('name')
        return '{} = {}\n{}'.format(lhs, rhs, self.annotate_srcloc(srcloc))

    def annotate_failure(self, step):
        srcloc = step.get('sourceLocation')
        reason = step['reason']
        return '<span class="failure">failure: {}</span>\n{}'.format(
            reason, self.annotate_srcloc(srcloc))

    def annotate_step(self, step):
        kind = step['stepType']
        fmt = '<span class="step">{}</span>\n'
        if kind == 'assignment':
            return fmt.format(self.annotate_assignment(step))
        if kind == 'failure':
            return fmt.format(self.annotate_failure(step))

        msg = "Skipping step type {}".format(kind)
        print(msg)
        logging.info(msg)
        logging.debug("Step is %s", step)
        return None

    def annotate_trace(self, trace):
        steps = [self.annotate_step(step) for step in trace]
        steps = [step for step in steps if step]
        return '\n'.join(steps)

    def generate_trace(self, error_name, error_trace, htmldir=None):
        """Generate an annotated trace file."""

        trace = []
        trace.append('<html><head><title>{err}</title></head>'
                     '<body><h1>{err}</h1>'
                     .format(err=error_name))
        trace.append('<div class="trace">')
        trace.append('Trace for {}:'.format(error_name))
        trace.append('<pre>')
        trace.append(self.annotate_trace(error_trace))
        trace.append('</pre>')
        trace.append('</div>')
        trace.append('</body></html>')

        tracedir = '{}/traces'.format(htmldir or 'html')
        try:
            os.makedirs(tracedir)
        except OSError:
            if not os.path.isdir(tracedir):
                raise

        tracefile = "{}/{}.html".format(tracedir, error_name)
        with open(tracefile, "w") as fp:
            fp.write("\n".join(trace))
