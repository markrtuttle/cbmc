"""Generate the list of source files used to build a goto binary."""

import sys
import logging
import os
import json
import subprocess
import re

################################################################

def sources_found_using_find(srcdir, srcexclude=None, proofdir=None):
    """Generate the list of source files with the Linux find command.

    All paths returned will begin with './'.  It would be cleaner to
    remove this prefix, but there is a long history of the regular
    expression srcexclude including this prefix.
    """

    try:
        cmd = ["find", "-L", ".",
               "(", "-iname", "*.[ch]", "-or", "-iname", "*.inl", ")"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=srcdir)
        return source_summary(srcdir, result.stdout.splitlines(), srcexclude, proofdir=proofdir)
    except subprocess.CalledProcessError:
        raise UserWarning('Failed to run command "{}"'.format(' '.join(cmd)))

################################################################

def sources_found_using_walk(srcdir, srcexclude=None, proofdir=None):
    """Generate the list of source files with the Python os.walk method.

    All paths returned will begin with './'.  It would be cleaner to
    remove this prefix, but there is a long history of the regular
    expression srcexclude including this prefix.

    This method is intended for use on Windows.  The os.walk method is
    more than three times slower than the find command, but find does
    not exist on Windows.
    """

    files = []
    cwd = os.getcwd()
    try:
        os.chdir(srcdir)
        for path, _, names in os.walk('.'):
            files.extend([os.path.join(path, name) for name in names])
    except FileNotFoundError:
        raise UserWarning('Source directory not found: {}'.format(srcdir))
    finally:
        os.chdir(cwd)
    return source_summary(srcdir, files, srcexclude, proofdir=proofdir)

################################################################

def sources_found_using_make(blddir='.', srcdir='.', proofdir=None):
    """Generate the list of source files with make.

    This method uses make and the goto-cc preprocessor to generate the
    list of files included by the preprocessor.  It assumes that 'make
    "GOTO_CC=goto-cc" goto' in blddir will build to goto binary.  It
    assumes the output on stdout contains all invocations of goto-cc
    used in the build.

    This method gives much better results than the methods using find
    or walk.  May projects include header files for many architectures
    defining architecture-specific values, and this method selects
    those actually used.  Many builds use only a tiny subset of the
    sources in the source tree, and this method selects those actually
    used.

    """

    logging.info('Running make in %s', blddir)
    blddir = os.path.abspath(blddir)
    # Preprocess and extract commands of form 'goto-cc -E -o file'
    bld_commands = build_with_preprocessor(blddir)
    logging.debug('Running make found build commands %s', bld_commands)
    bld_files = preprocessed_files(bld_commands, blddir)
    logging.debug('Running make found build files %s', bld_files)
    bld_output = preprocessed_output(bld_files)
    files = included_source_files(bld_output, blddir)
    logging.debug('Running make found source files %s', files)
    return source_summary(srcdir, files, proofdir=proofdir)

################################################################

def source_summary(srcdir, files, files_to_exclude=None, proofdir=None):
    """Select sources under source root and gather metrics."""

    logging.debug('source_summary srcdir: %s', srcdir)
    logging.debug('source_summary files: %s', files)
    logging.debug('source_summary files_to_exclude: %s', files_to_exclude)
    if files_to_exclude:
        files = [name for name in files
                 if not re.match(files_to_exclude, name)]
    files = [name for name in files
             if name.endswith(('.c', '.C', '.h', '.H', '.inl'))]
    files = [os.path.normpath(name) for name in files]
    root = os.path.abspath(srcdir)
    realroot = os.path.realpath(root)
    files = [name.replace(realroot, root) for name in files]
    files = sorted(list(set(files)))
    logging.debug('source_summary: files after processing %s', files)

    # In the special case where all files have relative pathnames,
    # we assume they are all relative to the source directory.

    all_full_paths = all([os.path.isabs(name) for name in files])
    all_relative_paths = all([not os.path.isabs(name) for name in files])
    if not (all_full_paths or all_relative_paths):
        raise UserWarning("Path not consistently absolute or relative")

    if all_full_paths:
        logging.info('Found files were full paths')
        full_paths, relative_paths = source_files_under_root(files, root)
        all_files = files
    if all_relative_paths:
        logging.info('Found files were relative paths')
        full_paths = [os.path.abspath(os.path.join(root, name))
                      for name in files]
        relative_paths = files
        all_files = full_paths

    results = {'root': root,
               'files': relative_paths,
               'lines-of-code': sloc(relative_paths, root),
               'root-files': full_paths,
               'all-files': all_files}

    if proofdir:
        proof_full_paths = [path for path in full_paths if proofdir in path]
        proof_relative_paths = [path for path in relative_paths if proofdir in path]
        results['proof-files'] = proof_relative_paths
        results['proof-root-files'] = proof_full_paths
        results['proof-lines-of-code'] = sloc(proof_relative_paths, root)

    return results

################################################################

def run_command(command, directory=None):
    """Run a command in a directory."""

    if isinstance(command, str):
        command = command.split()
    result = subprocess.run(command, capture_output=True, text=True,
                            cwd=directory)

    return result

################################################################

def build_with_preprocessor(directory=None):
    """Build the goto binary using goto-cc as a preprocessor."""

    logging.info('Doing "make clean" in %s', directory)
    run_command(['make', 'clean'], directory)
    logging.info('Doing "make GOTO_CC=goto-cc -E goto" in %s', directory)
    result = run_command(['make', 'GOTO_CC=goto-cc -E', 'goto'], directory)
    # Make will fail when it tries to link the preprocessed output
    # What is a system-independent way of skipping an okay link failure?
    logging.debug('Doing make generated result: %s', result)
    if result.returncode and result.returncode != 2:
        print(result.stdout)
        print(result.stderr)
        result.check_returncode()
    text = ' '.join(result.stdout.splitlines())
    lines = text.replace('goto-cc', '\ngoto-cc').splitlines()
    return [line for line in lines
            if line.strip().startswith('goto-cc')]

def preprocessed_files(commands, directory=None):
    """Accumulate the names of the files containing the preprocessed output."""

    files = []
    for cmd in commands:
        match = re.search(r' -o (\S+) ', cmd)
        if match:
            name = match.group(1)
            if directory:
                name = os.path.join(directory, name)
            files.append(os.path.abspath(name))
    return files

def preprocessed_output(files):
    """Accumulate the preprocessed output."""

    output = []
    for name in files:
        try:
            with open(name) as handle:
                output.extend(handle.read().splitlines())
        except FileNotFoundError:
            # The output file for the failed linking step will be in list
            logging.debug("Can't open '%s', "
                          "probably due to the failure of the link step", name)
    return output

def included_source_files(output, directory=None):
    """Extract the source file names listed in the preprocessed output."""

    files = [line.strip().split()[2] for line in output
             if line.strip().startswith('#')]
    files = [name.strip('"') for name in files]
    files = [name for name in files
             if name not in ['<built-in>', '<command']]
    if directory:
        files = [os.path.join(directory, name) for name in files]
    files = [os.path.abspath(name) for name in files]
    return sorted(list(set(files)))

################################################################

def source_files_under_root(files, root):

    """Extract the source files under the root."""

    full = [name for name in files if name.startswith(root)]
    relative = [name[len(root):].lstrip(os.sep) for name in full]
    return sorted(list(set(full))), sorted(list(set(relative)))

################################################################

def sloc(files, root=None):
    """Run sloc on files under the root directory."""

    if not files:
        raise UserWarning("No source files for sloc.")

    command = ['sloc', '-f', 'json'] + files
    try:
        result = run_command(command, root)
    except OSError as error:
        if error.errno == 7: # 'Argument list too long'
            return None
    if result.returncode:
        sys.stderr.write("\nsloc failed, skipping sloc statistics\n\n")
        logging.debug("sloc failed, ignoring sloc statistics")
        logging.debug("sloc standard output was:")
        logging.debug(result.stdout)
        logging.debug("sloc standard error is:")
        logging.debug(result.stderr)
        return None
    # sloc produces a great deal of useful data in addition to the summary
    return json.loads(result.stdout)["summary"]


################################################################

def merge(data_files):
    """Merge a collection of files produced by this program."""

    root = None
    all_files = []
    for data_file in data_files:
        with open(data_file) as data_json:
            data = json.load(data_json)
            data_root = os.path.abspath(data['root'])
            data_all_files = data['all-files']
            if root is None:
                root = data_root
            elif root != data_root:
                raise UserWarning('Found differing roots {} and {}'.
                                  format(root, data_root))
            all_files.extend(data_all_files)
    all_files = sorted(list(set(all_files)))
    root_files, files = source_files_under_root(all_files, root)
    return {'root': root,
            'files': files,
            'lines-of-code': sloc(files, root),
            'root-files': root_files,
            'all-files': all_files}

################################################################
