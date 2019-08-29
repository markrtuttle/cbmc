"""Mark up the source tree and links into the source tree."""

import sys
import html
import os
import re
import errno

import linestatus
import comment

class Markup:
    """Mark up the source tree and links into the source tree."""

    def __init__(self, symbols, coverage,
                 srcdir=".", htmldir="html", srcfilter="", sources=None):
        """Initialize marking up the source tree."""
        # pylint: disable=too-many-arguments
        self.symbols = symbols
        self.coverage = coverage
        self.srcdir = srcdir.rstrip('/')
        self.htmldir = htmldir.rstrip('/')
        self.srcfilter = srcfilter
        self.sources = sources

    @staticmethod
    def src_html(src):
        """Map a source file path to the corresponding html file path."""
        return src+".html"

    def link_to_line(self, src, line, text, depth=0, target=None):
        """Link text to a line in a source file."""

        path = directory_ancestor(depth) + '/' + self.src_html(src)
        line = '#{}'.format(line) if line else ''
        tgt = ' target="{}"'.format(target) if target else ''
        return '<a href="{}{}"{}>{}</a>'.format(path, line, tgt, text)

    def link_to_file(self, text, src, depth=0, target=None):
        """Link text to a source file."""
        # pylint: disable=too-many-arguments
        return self.link_to_line(src, 0, text, depth, target)

    def link_symbol(self, symbol, depth=0, target=None, text=None):
        """Link a symbol to its definition."""
        # pylint: disable=too-many-arguments
        val = self.symbols.lookup(symbol)
        if not val:
            return symbol

        text = text or symbol
        (src, line) = val
        return self.link_to_line(src, line, text, depth, target)

    def link_file(self, src, depth=0):
        """Link a source file to its html file."""
        return self.link_to_file(src, src, depth)

    def link_function(self, function, depth=0):
        """Link a function to its definition."""
        return self.link_symbol(function, depth)

    def markup_source_location(self, loc, depth=0, target=None):
        # pylint: disable=too-many-locals
        """Link trace source location to file, line, and function."""

        match = re.search('(file ([^ ]+)) (function ([^ ]+)) (line ([^ ]+))', loc,
                          re.IGNORECASE)

        if not match:
            return loc

        file_text = match.group(1)
        file_text_start = match.start(1)
        file_text_end = match.end(1)
        file_name = match.group(2)
        file_link = self.link_to_file(file_text, file_name, depth, target)

        func_text = match.group(3)
        func_text_start = match.start(3)
        func_text_end = match.end(3)
        func_name = match.group(4)
        func_link = self.link_symbol(func_name, depth, target, func_text)

        line_text = match.group(5)
        line_text_start = match.start(5)
        line_text_end = match.end(5)
        line_num = match.group(6)
        line_link = self.link_to_line(file_name, line_num, line_text,
                                      depth, target)

        if file_name[0] == '<' and file_name[-1] == '>':
            return html.escape(loc, quote=False)

        return (loc[:file_text_start] + file_link +
                loc[file_text_end:func_text_start] + func_link +
                loc[func_text_end:line_text_start] + line_link +
                loc[line_text_end:])

    @staticmethod
    def read_source_file(srcfile):
        """Read source file contents and clean up whitepsace."""

        # Read file using latin-1 encode.  Some files created on
        # Windows in Europe appear to use latin-1 and not ascii or
        # utf-8.  All three are compatible on the ascii character set.
        # But remember that Python latin-1 is slightly different from
        # what Windows calls latin-1.
        with open(srcfile, encoding="latin-1") as handle:
            lines = handle.read().splitlines()
            lines = [untabify(line).rstrip() for line in lines]
            return '\n'.join(lines)

    def write_html_file(self, title, contents, htmlfile, depth, coverage):
        """Write soure file contents as html annotated with coverage."""

        def markup_segment(segment, depth):
            if not comment.code_start(segment):
                return segment
            tokens = re.split('([_a-zA-Z][_a-zA-Z0-9]*)', segment)
            return "".join([self.link_symbol(token, depth) for token in tokens])

        contents = html.escape(contents, quote=False)
        segments = comment.parse(contents)
        segments = [markup_segment(segment, depth) for segment in segments]
        contents = ''.join(segments)

        try:
            os.makedirs(os.path.dirname(htmlfile))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        coverage = coverage or {}
        with open(htmlfile, "w") as handle:
            html_header(handle, title, depth)
            lineno = 0
            for line in contents.splitlines():
                lineno += 1
                html_line(handle, line, lineno, coverage.get(lineno))
            html_footer(handle)

    def markup_file(self, indir, infile, outfile, depth, coverage):
        """Mark up a source file with links to symbol definitions."""

        contents = self.read_source_file(infile)
        title = infile
        if title.startswith(indir):
            title = title[len(indir):].lstrip(os.sep)
        self.write_html_file(title, contents, outfile, depth, coverage)

    def markup_directory(self):
        """Mark up a source directory with links to symbol definitions."""
        try:
            os.makedirs(self.htmldir)
        except OSError as e:
            if not os.path.isdir(self.htmldir):
                print("Can't make directory {}: {}".format(self.htmldir,
                                                           e.strerror))
                sys.exit()
            if e.errno != errno.EEXIST:
                raise

        html_css(self.htmldir)
        for src in self.sources.files():
            if src == '':
                continue
            if src[0] == '/':
                continue
            self.markup_file(self.srcdir,
                             os.path.join(self.srcdir, src),
                             os.path.join(self.htmldir, self.src_html(src)),
                             directory_depth(src),
                             self.coverage.line.get(src))

################################################################


def untabify(string, tabstop=8):
    """Replace tabs with spaces in a line of code."""
    parts = re.split('(\t)', string)
    result = ''
    for s in parts:
        if s == '\t':
            result += ' '*(tabstop - (len(result) % tabstop))
            continue
        result += s
    return result

################################################################


def directory_depth(path):
    """Compute number of directories appearing in a path.

    The depth of dir1/dir2/dir3/file.c is 3.
    """
    path = os.path.normpath(path.strip())
    return len(path.split('/'))-1

def directory_ancestor(depth):
    # pylint: disable=unused-variable
    """Compute path to the ancestor the given number of levels up.

    The directory redirection of depth 3 is ../../..
    """
    if depth < 1:
        return '.'
    return '/'.join(['..' for n in range(depth)])

################################################################


def html_header(fp, title, depth=0):
    """Write the html header to a file."""
    fp.write("<html>\n")
    fp.write("<head>\n")
    fp.write("<title>"+title+"</title>\n")
    fp.write('<link rel="stylesheet" href="{}/style.css">\n'
             .format(directory_ancestor(depth)))
    fp.write("</head>\n")
    fp.write("<body><pre>\n")


def html_footer(fp):
    """Write the html footer to a file."""
    fp.write("</pre></body>\n</html>\n")


def html_line(fp, line, lineno, ls=None):
    """Write the annotated source line to an html file.
    """
    class_map = {
        linestatus.HIT: ' class="hit"',
        linestatus.MISSED: ' class="missed"',
        linestatus.PARTIAL: ' class="partial"'
        }
    fp.write('<span id="{lineno}"{cls}>{lineno:5} {line}</span>\n'.
             format(lineno=lineno, cls=class_map.get(ls, ''), line=line))

css = """
.hit,
.hit a
{
    color: green;
}

.missed,
.missed a
{
    color: red;
}

.partial,
.partial a
{
    color: orange;
}
"""

def html_css(root):
    """Write style file into the root html directory."""
    with open('{}/style.css'.format(root), 'w') as cssfile:
        cssfile.write(css)

################################################################
