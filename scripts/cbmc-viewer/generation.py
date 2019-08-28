import json
import os

root = '/Users/mrtuttle/freertos'

################################################################

def step_id(sid):
    return '.'.join([str(lid) for lid in sid])

def step_id_increment(sid):
    sid[-1] += 1
    return sid

def step_id_increase(sid):
    return sid + [0]

def step_id_decrease(sid):
    return sid[:-1]

def block_id(sid):
    return 'block-'+step_id(sid)

################################################################

def link_srcloc(srcloc):
    if srcloc is None:
        return " "
    line = srcloc['line']
    path = srcloc['file']
    if path.startswith('<') and path.endswith('>'):
        return " "
    path = os.path.join(srcloc['workingDirectory'], path)
    path = os.path.normpath(path)
    if not path.startswith(root):
        return " "
    path = os.path.join('..', path[len(root):].strip(os.sep))
    return '<a class="source" href="{}#{}">></a>'.format(path, line)

################################################################

def start_block(sid):
    return ('<div class="block" onclick="expandBlock(event)" id="{}">'
            .format(block_id(sid)))

def end_block():
    return '</div>'

################################################################

def expand_button():
    return '<span onclick="expandButton(event)">+</span>'

def collapse_button():
    return '<span onclick="collapseButton(event)">-</span>'

def focus_button():
    return '<span onclick="focusButton(event)">*</span>'

def unfocus_button():
    return '<span onclick="unfocusButton(event)">**</span>'

def step_line(sid, srcloc, indent, text):
    line = '<span class="line" id="{}">'.format(step_id(sid))
    line += collapse_button() + ' '
    line += expand_button() + ' '
    line += focus_button() + ' '
    line += unfocus_button() + ' '
    line += link_srcloc(srcloc) + ' '
    line += indent
    line += text
    line += '</span>'
    return line

################################################################

def main():
    with open('trace.json') as handle:
        trace = json.load(handle)["trace"]

    print('<html><head>')
    print('<link rel="stylesheet" href="cbmc-viewer.css">')
    print('<script type="text/javascript" src="cbmc-viewer.js"></script>')
    print('</head><body><div class="trace">', end='')

    sid = [0]
    indent = ''
    for step in trace:

        kind = step['stepType']
        if kind == 'location-only':
            continue

        if kind == 'function-return':
            sid = step_id_decrease(sid)
            indent = indent[:-4]

        string = None

        if kind == 'assignment':
            lhs = step['lhs']
            if lhs.startswith('__CPROVER_'):
                continue
            value = step['value']
            data = value.get('data')
            name = value.get('name')
            data = data if data is not None else name
            string = '{} = {}'.format(lhs, data)

        if kind == 'failure':
            string = kind + ': ' + step['reason']

        if kind == 'function-call':
            try:
                caller = step['sourceLocation']['function']
            except KeyError:
                caller = None
            try:
                callee = step['function']['displayName']
            except KeyError:
                callee = None
            string = 'function call: {} -> {}'.format(caller, callee)

        if kind == 'function-return':
            try:
                callee = step['sourceLocation']['function']
            except KeyError:
                callee = None
            string = 'function return: <- {}'.format(callee)

        sid = step_id_increment(sid)
        string = string or kind

        if kind == 'function-return':
            print(end_block(), end='')


        print()
        print(step_line(sid, step.get('sourceLocation'), indent, string),
              end='')

        if kind == 'function-call':
            print(start_block(sid), end='')

        if kind == 'function-call':
            sid = step_id_increase(sid)
            indent += '    '

    print('</div></body></html>')




if __name__ == '__main__':
    main()
