import re
import os
import logging

import markupt

################################################################

class CodeSnippet:
    def __init__(self, root):
        self.root = root
        self.source = {}

    def lookup(self, path, line):
        if line <= 0: # line numbers are 1-based
            logging.info("CodeSnippet lookup: line number not positive: %s",
                         line)
            return None
        line -= 1    # list indices are 0-based

        try:
            if path not in self.source:
                with open(os.path.join(self.root, path)) as code:
                    self.source[path] = code.read().splitlines()
        except FileNotFoundError:
            logging.info("CodeSnippet lookup: file not found: %s", path)
            return None

        snippet = ' '.join(self.source[path][line:line+5])
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        loc = snippet.find(';')
        if loc >= 0:
            return snippet[:loc+1]
        loc = snippet.find('}')
        if loc >= 0:
            return snippet[:loc+1]
        return snippet


    def lookup_srcloc(self, srcloc):
        return self.lookup(srcloc['file'], srcloc['line'])

################################################################

class MarkupTrace:
    def __init__(self, sources, symbols, traces, htmldir='html'):
        self.sources = sources
        self.symbols = symbols
        self.traces = traces
        self.snippet = CodeSnippet(sources.root)
        self.htmldir = htmldir

    def markup_traces(self):
        os.makedirs(os.path.join(self.htmldir, 'traces'), exist_ok=True)
        for name, trace in self.traces.traces.items():
            self.markup_trace(name, trace)

    def markup_trace(self, name, trace):
        html = []
        for num, step in enumerate(trace):
            html.append(self.markup_step(step, num+1))
        with open(os.path.join(self.htmldir, 'traces', '{}.html'.format(name)), 'w') as data:
            data.write(HTML.format(name=name, trace='\n'.join(html)))

    def markup_step(self, step, num=0):
        srcloc = self.markup_srcloc(step['location'])
        code = self.snippet.lookup_srcloc(step['location'])
        #code = markupt.link_symbols_in_text(
        #    code, self.symbols, from_file='./trace/trace.html'
        #)
        markup = {
            "function-call": markup_function_call,
            "function-return": markup_function_return,
            "variable-assignment": markup_variable_assignment,
            "parameter-assignment": markup_parameter_assignment,
            "assumption": markup_assumption,
            "failure": markup_failure
        }[step['kind']]
        cbmc = markup(step)
        #cbmc = markupt.link_symbols_in_text(
        #    cbmc, self.symbols, from_file='./trace/trace.html'
        #)

        html = []

        if step['kind'] == 'function-call':
            html.append('<div class="function">')
            html.append('<div class="function-call">')

        if step['kind'] == 'function-return':
            html.append('</div>') # end function-body
            html.append('<div class="function-return">')

        html.append('<div id="step{}" class="step">'.format(num))
        html.append('<div class="header">Step {}: {}</div>'.format(num, srcloc))
        if code:
            html.append('<div class="code">{}</div>'.format(code))
        html.append('<div class="cbmc">{}</div>'.format(cbmc))
        html.append('</div>')

        if step['kind'] == 'function-call':
            html.append('</div>') # end function-call
            html.append('<div class="function-body">')

        if step['kind'] == 'function-return':
            html.append('</div>') # end function-return
            html.append('</div>') # end function

        return '\n'.join(html)

    def markup_srcloc(self, srcloc):
        fyle, func, line = srcloc['file'], srcloc['function'], srcloc['line']
        return 'Function {}, File {}, Line {}'.format(
            markupt.link_text_to_srcloc(func, self.symbols.lookup(func), './trace/trace.html'),
            markupt.link_text_to_file(fyle, fyle, './trace/trace.html'),
            markupt.link_text_to_line(line, fyle, line, './trace/trace.html')
        )

################################################################

def markup_function_call(step):
    name, srcloc = step['detail']['name'], step['detail']['location']

    line = '-> {}'.format(
        markupt.link_text_to_srcloc(name, srcloc, './trace/trace.html')
    )
    return line

def markup_function_return(step):
    name, srcloc = step['detail']['name'], step['detail']['location']
    line = '<- {}'.format(
        markupt.link_text_to_srcloc(name, srcloc, './trace/trace.html')
    )
    return line

def markup_variable_assignment(step):
    asn = step['detail']
    lhs, rhs, binary = asn['lhs'], asn['rhs-value'], asn['rhs-binary']
    binary = '({})'.format(binary) if binary else ''
    return '{} = {} {}'.format(lhs, rhs, binary)

def markup_parameter_assignment(step):
    asn = step['detail']
    lhs, rhs, binary = asn['lhs'], asn['rhs-value'], asn['rhs-binary']
    binary = '({})'.format(binary) if binary else ''
    return '{} = {} {}'.format(lhs, rhs, binary)

def markup_assumption(step):
    pred = step['detail']['predicate']
    return 'assumption: {}'.format(pred)

def markup_failure(step):
    prop = step['detail']['property'] or "Unnamed"
    reason = step['detail']['reason'] or "Not given"
    return 'failure: {}: {}'.format(prop, reason)

################################################################

HTML = """
<html>
<head>
<title>Trace for {name}</title>
<link rel="stylesheet" type="text/css" href="../viewer.css">
</head>

<body>
<div class="trace">
<h2>Trace for {name}</h2>
{trace}
</div>
</body>
<script type="text/javascript" src="../viewer.js"></script>
</html>
"""
