import json
import os

root = '/Users/mrtuttle/freertos'

def step_id(sid):
    return '.'.join([str(lid) for lid in sid])

def step_increment(sid):
    sid[-1] += 1
    return sid

def step_increase(sid):
    return sid + [0]

def step_decrease(sid):
    return sid[:-1]

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
    return '<a style="text-decoration: none; color: inherit;" href="{}#{}">></a>'.format(path, line)

def block_id(sid):
    return 'block-'+step_id(sid)

def start_block(sid, indent):
    print(indent + '<div class="block" onclick="event.currentTarget.style.display=\'inline\'" style="display: inline" id="{}">'.format(block_id(sid)), end='')

def end_block(indent):
    print(indent + '</div>', end='')

def expand_button(sid):
    return '<span id="expand-{}" onclick="document.getElementById(\'{}\').style.display=\'inline\'; event.stopPropagation()">+</span>'.format(block_id(sid), block_id(sid))

def collapse_button(sid):
    return '<span id="collapse-{}" onclick="event.target.closest(\'.block\').style.display=\'none\'; event.stopPropagation()">-</span>'.format(block_id(sid),block_id(sid))

def star_button(sid):
    return '<span id="star-{}" onclick="for (elt of document.getElementsByClassName(\'block\')) elt.style.display=\'none\'; event.target.click();">*</span>'.format(block_id(sid))

def starstar_button(sid):
    return '<span id="starstar-{}" onclick="for (elt of document.getElementsByClassName(\'block\')) elt.style.display=\'inline\'">**</span>'.format(block_id(sid))

def show_step(sid, srcloc, indent, string):
    line = '<span id="{}">'.format(step_id(sid))
    line += collapse_button(sid) + ' '
    line += expand_button(sid) + ' '
    line += star_button(sid) + ' '
    line += starstar_button(sid) + ' '
    line += link_srcloc(srcloc) + ' '
    line += indent
    line += string
    line += '</span>'
    print('\n'+line, end='')

def main():
    with open('trace.json') as handle:
        trace = json.load(handle)["trace"]


    print('<html><body><pre>')

    sid = [0]
    indent = ''
    for step in trace:

        kind = step['stepType']
        if kind == 'location-only':
            continue

        if kind == 'function-return':
            sid = step_decrease(sid)
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

        sid = step_increment(sid)
        string = string or kind

        if kind=='function-return':
            end_block(indent)


        show_step(sid, step.get('sourceLocation'), indent, string)

        if kind=='function-call':
            start_block(sid, indent)

        if kind == 'function-call':
            sid = step_increase(sid)
            indent += '    '

    print('</pre></body></html>')




if __name__ == '__main__':
    main()

