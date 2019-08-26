"""Generate the list of source files used to build a goto binary."""

import logging
import os
import json
import subprocess
import re

################################################################

def sources_found_using_find(srcdir, srcexclude=None):
    """Generate the list of source files with the Linux find command.

    All paths returned will begin with './'.  It would be cleaner to
    remove this prefix, but there is a long history of the regular
    expression srcexclude including this prefix.
    """

    try:
        cmd = ["find", "-L", ".",
               "(", "-iname", "*.[ch]", "-or", "-iname", "*.inl", ")"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=srcdir)
        return source_summary(srcdir, result.stdout.splitlines(), srcexclude)
    except subprocess.CalledProcessError:
        raise UserWarning('Failed to run command "{}"'.format(' '.join(cmd)))

################################################################

def sources_found_using_walk(srcdir, srcexclude=None):
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
    return source_summary(srcdir, files, srcexclude)

################################################################

def sources_found_using_make(blddir='.', srcdir='.'):
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

    blddir = os.path.abspath(blddir)
    # Preprocess and extract commands of form 'goto-cc -E -o file'
    bld_commands = build_with_preprocessor(blddir)
    bld_files = preprocessed_files(bld_commands, blddir)
    bld_output = preprocessed_output(bld_files)
    files = included_source_files(bld_output, blddir)
    return source_summary(srcdir, files)

################################################################

def source_summary(srcdir, files, files_to_exclude=None):
    """Select sources under source root and gather metrics."""

    root = os.path.abspath(srcdir)
    if files_to_exclude:
        files = [name for name in files
                 if not re.match(files_to_exclude, name)]
    files = [name for name in files
             if name.endswith(('.c', '.C', '.h', '.H', '.inl'))]
    files = sorted(list(set(files)))
    files = [os.path.normpath(name) for name in files]

    # In the special case where all files have relative pathnames,
    # we assume they are all relative to the source directory.

    all_full_paths = all([os.path.isabs(name) for name in files])
    all_relative_paths = all([not os.path.isabs(name) for name in files])
    if not (all_full_paths or all_relative_paths):
        raise UserWarning("Path not consistently absolute or relative")

    if all_full_paths:
        full_paths, relative_paths = source_files_under_root(files, root)
        all_files = files
    if all_relative_paths:
        full_paths = [os.path.abspath(os.path.join(root, name))
                      for name in files]
        relative_paths = files
        all_files = full_paths

    return {'root': root,
            'files': relative_paths,
            'lines-of-code': sloc(relative_paths, root),
            'root-files': full_paths,
            'all-files': all_files}

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

    run_command(['make', 'clean'], directory)
    result = run_command(['make', 'GOTO_CC=goto-cc -E', 'goto'], directory)
    # Make will fail when it tries to link the preprocessed output
    # What is a system-independent way of skipping an okay link failure?
    if result.returncode and result.returncode != 2:
        print(result.stdout)
        print(result.stderr)
        result.check_returncode()
    return [line for line in result.stdout.splitlines()
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

    root = os.path.abspath(root)
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
        print(result.stdout)
        print(result.stderr)
        result.check_returncode()
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
