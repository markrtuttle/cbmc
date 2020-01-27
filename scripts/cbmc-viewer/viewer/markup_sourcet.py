import re
import os

import markupt

################################################################

def depth_from_root(path):
    return len([char for char in path if char == '/'])

def path_to_root(path):
    return os.path.normpath(
        '/'.join(['..' for level in range(depth_from_root(path))])
    )

################################################################

class MarkupSource:
    def __init__(self, sources, symbols, coverage, htmldir=None):
        self.sources = sources
        self.symbols = symbols
        self.coverage = coverage
        self.htmldir = htmldir or 'html'

    def markup_code(self, path, code):
        code = untabify_code(code)
        blocks = split_code_into_code_blocks(code)
        blocks = link_symbols_in_code_blocks(path, blocks, self.symbols)
        code = ''.join(blocks)
        code = annotate_code(path, code, self.coverage)
        return html_from_code(path, code)

    def markup_files(self, root, files):
        for path in files:
            self.markup_file(root, path)

    def markup_file(self, root, path):
        with open(os.path.join(root, path)) as source:
            code = self.markup_code(path, source.read())
        pathname = os.path. join(self.htmldir, path+".html")
        os.makedirs(os.path.dirname(pathname), exist_ok=True)
        with open(pathname, "w") as html:
            html.write(code)

################################################################
# Untabify code: replace tabs with spaces.

def untabify_code(code, tabstop=8):
    """Untabify a block of code."""

    return '\n'.join(
        [untabify_line(line, tabstop) for line in code.splitlines()]
    )

def untabify_line(line, tabstop=8):
    """Untabify a line of code."""

    parts = re.split('(\t)', line)
    result = ''
    for part in parts:
        if part == '\t':
            result += ' '*(tabstop - (len(result) % tabstop))
            continue
        result += part
    return result

################################################################
# Split code into code blocks and strings/comments

def split_code_into_code_blocks(code):

    def is_noncode_start(code, idx=0):
        return (is_quote(code, idx) or
                is_multiline_comment_start(code, idx) or
                is_singleline_comment_start(code, idx))

    def find_predicate(code, predicate, loc=0):
        while loc < len(code) and not predicate(code, loc):
            loc += 1
        return loc

    blocks = []

    while code:
        loc = find_predicate(code, is_noncode_start)
        block, code, loc = code[:loc], code[loc:], 0
        if block:
            blocks.append(block)

        if not code:
            break

        if is_quote(code):
            loc = find_predicate(code, is_quote, 1)
        if is_multiline_comment_start(code):
            loc = find_predicate(code, is_multiline_comment_end, 2)
        if is_singleline_comment_start(code):
            loc = find_predicate(code, is_singleline_comment_end, 2)
        block, code, loc = code[:loc+1], code[loc+1:], 0
        if block:
            blocks.append(block)

    return blocks

def is_quote(code, idx=0):
    return (0 <= idx < len(code) and
            code[idx] == '"' and
            (idx == 0 or code[idx-1] != '\\'))

def is_multiline_comment_start(code, idx=0):
    return idx >= 0 and idx+2 <= len(code) and code[idx:idx+2] == '/*'

def is_multiline_comment_end(code, idx=0):
    return idx-1 >= 0 and idx+1 <= len(code) and code[idx-1:idx+1] == '*/'

def is_singleline_comment_start(code, idx=0):
    return idx >= 0 and idx+2 <= len(code) and code[idx:idx+2] == '//'

def is_singleline_comment_end(code, idx=0):
    return idx >= 0 and idx+1 < len(code) and code[idx+1] == '\n'

################################################################
# Link symbols in code blocks

def link_symbols_in_code_blocks(path, blocks, symbols):
    return [link_symbols_in_code_block(path, block, symbols)
            for block in blocks]

def link_symbols_in_code_block(path, block, symbols):
    if (is_quote(block) or
            is_multiline_comment_start(block) or
            is_singleline_comment_start(block)):
        return block

    return link_symbols(path, block, symbols)

def link_symbols(path, code, symbols):
    tokens = split_code_into_symbols(code)
    return ''.join(
        [markupt.link_text_to_symbol(tkn, tkn, symbols, from_file=path)
         for tkn in tokens]
    )

def split_code_into_symbols(code):
    return re.split('([_a-zA-Z][_a-zA-Z0-9]*)', code)

################################################################
# Annotate code with line numbers and coverage

def annotate_code(path, code, coverage):
    num = 0
    lines = []
    for line in code.splitlines():
        num += 1
        lines.append(
            '<div id="{num}" class="line {hit}">{num:5} {line}</div>'
            .format(num=num,
                    hit=coverage.lookup(path, num) or "none",
                    line=line)
        )
    return '\n'.join(lines)

################################################################

def html_from_code(path, code):
    html = """
<html>
<head>
<title>{path}</title>
<link rel="stylesheet" type="text/css" href="{root}/viewer.css">
</head>

<body>
<div class="code">
{code}
</div>
</body>
</html>
"""
    return html.format(path=path, root=path_to_root(path), code=code)
