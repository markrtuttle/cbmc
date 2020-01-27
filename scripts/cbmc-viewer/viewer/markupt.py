"""Links to source code.

This module is a set of methods for constructing links into the
annotated source code.  All other modules use these methods for
consistent links to source code.  All paths in this module are
assumed to be relative to the root of the source code.

"""

import re
import os
import html

import locationt

def normpath(path):
    """A well-formed path to a source file in the source tree."""

    return locationt.canonical_path(path or '.')

def depth_from_root(path):
    """The depth of a source file from the root of the source tree."""

    path = normpath(path)
    return len([char for char in path if char == '/'])

def path_to_root(path):
    """The relative path from a source file to the root of the source tree."""

    depth = depth_from_root(path)
    result = os.path.join('.', *['..' for level in range(depth)])
    return normpath(result)

def path_to_file(to_path, from_path=None):
    """The relative path from one source file to another in the source tree."""

    from_path = from_path or to_path
    result = os.path.join(path_to_root(from_path), to_path)
    return normpath(result)

################################################################
# Method to link into the source tree.
# By default, links are from the root of the source tree to the source file.

def link_text_to_file(text, to_file, from_file=None):
    """Link text to a file in the source tree."""

    if locationt.builtin_name(to_file):
        return html.escape(str(text))

    from_file = from_file or '.'
    path = path_to_file(to_file, from_file)
    return '<a href="{}.html">{}</a>'.format(path, text)

def link_text_to_line(text, to_file, line, from_file=None):
    """Link text to a line in a file in the source tree."""

    if locationt.builtin_name(to_file):
        return html.escape(str(text))

    from_file = from_file or '.'
    line = int(line)
    path = path_to_file(to_file, from_file)
    return '<a href="{}.html#{}">{}</a>'.format(path, line, text)

def link_text_to_srcloc(text, srcloc, from_file=None):
    """Link text to a source location in a file in the source tree."""

    if srcloc is None:
        return text
    return link_text_to_line(text, srcloc['file'], srcloc['line'], from_file)

def link_text_to_symbol(text, symbol, symbols, from_file=None):
    """Link text to a symbol definition in the source tree."""

    srcloc = symbols.lookup(symbol)
    return link_text_to_srcloc(text, srcloc, from_file)

def split_text_into_symbols(text):
    """Split text into substrings that could be symbols."""

    return re.split('([_a-zA-Z][_a-zA-Z0-9]*)', text)

def link_symbols_in_text(text, symbols, from_file=None):
    """Link symbols appearing in text to their definitions."""

    if text is None:
        return None

    tokens = split_text_into_symbols(text)
    return ''.join(
        [link_text_to_symbol(tkn, tkn, symbols, from_file)
         for tkn in tokens]
    )

################################################################
