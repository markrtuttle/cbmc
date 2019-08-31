import os
import subprocess
import json
import logging

def run_goto_analyzer(goto):
    cmd = ['goto-analyzer', '--reachable-functions', '-json', '-', goto]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        logging.info("Command failed: %s", ' '.join(result.args))
        logging.debug("stdout is")
        logging.debug(result.stdout)
        logging.debug("stderr is")
        logging.debug(result.stderr)
        result.check_returncode()
    # skip 6 lines of text printed before the json
    logging.info("Command succeeded: %s", ' '.join(result.args))
    logging.debug("stdout is")
    logging.debug(result.stdout)
    return '\n'.join(result.stdout.splitlines()[6:])

def goto_analyzer_results(goto):
    reachable = json.loads(run_goto_analyzer(goto))
    functions = []
    for function in reachable:
        path = os.path.normpath(function['file name'])
        name = os.path.basename(path)
        # skip functions internal to cbmc
        if name.startswith('<') and name.endswith('>'):
            logging.info('Skipping internal function %s', name)
            continue
        function['file name'] = path
        functions.append(function)
    functions = sorted(functions, key=lambda func: func['function'])
    logging.debug('Reachable functions found by goto-analyzer')
    logging.debug(functions)
    return functions

def reachable_functions(goto):
    data = goto_analyzer_results(goto)
    functions = [func['function'] for func in data]
    logging.info('Reachable functions found: %s', functions)
    return {'functions': functions,
            'data': data}
