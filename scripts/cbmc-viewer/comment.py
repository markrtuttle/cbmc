"""Parse comments and strings out of code.

Break a string of code up into fragments of code and comments
and strings so that only code fragements will be marked up with
links to symbols.
"""

################################################################

def single_quote_start(line, cur):
    """True if cur points to start of a single quote in line."""
    return cur < len(line) and line[cur] == "'"

def single_quote_end(line, cur):
    """True if cur points to end of a single quote in line."""
    return (cur < len(line) and line[cur] == "'" and
            # line[cur-1] == \  => line[cur-2] == \
            (not (cur > 0 and line[cur-1] == '\\') or
             (cur > 1 and line[cur-2] == '\\')))

def double_quote_start(line, cur):
    """True if cur points to start of a double quotate in line."""
    return cur < len(line) and line[cur] == '"'

def double_quote_end(line, cur):
    """True if cur points to end of a double quotate in line."""
    return (cur < len(line) and line[cur] == '"' and
            # line[cur-1] == \  => line[cur-2] == \
            (not (cur > 0 and line[cur-1] == '\\') or
             (cur > 1 and line[cur-2] == '\\')))

def multiline_comment_start(line, cur):
    """True if cur points to start of a multi-line comment in line."""
    return cur + 1 < len(line) and line[cur] == '/' and line[cur+1] == '*'

def multiline_comment_end(line, cur):
    """True if cur points to end of a multi-line comment in line."""
    return 0 < cur < len(line) and line[cur-1] == '*' and line[cur] == '/'

def oneline_comment_start(line, cur):
    """True if cur points to start of a one-line comment in line."""
    return cur + 1 < len(line) and line[cur] == '/' and line[cur+1] == '/'

def oneline_comment_end(line, cur):
    """True if cur points to end of a one-line comment in line."""
    return cur+1 < len(line) and line[cur+1] == '\n'

def scan_to_end(predicate, line, cur):
    """Scan from current position to next position satsifying a predicate."""
    while cur < len(line) and not predicate(line, cur):
        cur += 1
    if cur >= len(line):
        cur = len(line)
    return cur

def parse_to_end(predicate, line, start, cur, results):
    """Parse from current poition to next position satisfying a predicate."""

    if not start < len(line) or not cur < len(line):
        raise ValueError

    # Retain portion of line coming before current token
    if start < cur:
        results.append(line[start:cur])

    start = cur
    cur = scan_to_end(predicate, line, cur+1) + 1
    results.append(line[start:cur])

    return (cur, cur, results)

def parse(line):
    """Parse a line of code into fragments of comments, strings, and code."""
    start = 0
    cur = 0
    results = []

    while cur < len(line):
        if single_quote_start(line, cur):
            start, cur, results = parse_to_end(single_quote_end,
                                               line, start, cur, results)
            continue
        if double_quote_start(line, cur):
            start, cur, results = parse_to_end(double_quote_end,
                                               line, start, cur, results)
            continue
        if multiline_comment_start(line, cur):
            start, cur, results = parse_to_end(multiline_comment_end,
                                               line, start, cur, results)
            continue
        if oneline_comment_start(line, cur):
            start, cur, results = parse_to_end(oneline_comment_end,
                                               line, start, cur, results)
            continue
        cur += 1

    if start < cur:
        results.append(line[start:cur])
    return results

def code_start(line, cur=0):
    """True if current position is the start of a code segment."""
    return not (single_quote_start(line, cur) or
                double_quote_start(line, cur) or
                multiline_comment_start(line, cur) or
                oneline_comment_start(line, cur))
