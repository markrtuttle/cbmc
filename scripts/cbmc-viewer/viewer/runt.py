import logging
import subprocess

def run(cmd, cwd=None, ignored=None, verbose=False):
    """Run a command in a directory.  Ignore a list of return codes. """

    logging.debug('cmd: %s, cwd: %s, ignored: %s, verbose: %s',
                  cmd, cwd, ignored, verbose)

    if isinstance(cmd, str):
        cmd = cmd.split()
    if verbose:
        print('Running: {}'.format(' '.join(cmd)))

    result = subprocess.run(cmd, cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)

    if result.returncode:
        logging.debug('Error running command. %s', result)
        if ignored is None or result.returncode not in ignored:
            result.check_returncode()

    return result.stdout
