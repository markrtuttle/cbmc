#!/usr/bin/env python3

import json

################################################################

def model_lines(viewer_coverage, proof_root=None):
    lines = [(path, int(line))
             for path, func_data in viewer_coverage['coverage'].items()
             for func, line_data in func_data.items()
             for line, status in line_data.items()
             if proof_root and path.startswith(proof_root)]
    return sorted(set(lines))

def project_lines(viewer_coverage, proof_root=None):
    lines = [(path, int(line))
             for path, func_data in viewer_coverage['coverage'].items()
             for func, line_data in func_data.items()
             for line, status in line_data.items()
             if not (proof_root and path.startswith(proof_root))]
    return sorted(set(lines))

def project_lines_hit(viewer_coverage, proof_root=None):
    lines = [(path, int(line))
             for path, func_data in viewer_coverage['coverage'].items()
             for func, line_data in func_data.items()
             for line, status in line_data.items()
             if not (proof_root and path.startswith(proof_root))
             and status != 'missed']
    return sorted(set(lines))

################################################################

def property_issue_lines(failures, properties):
    props = [fail for fail in failures if fail in properties]

    prop_file = lambda prop: properties[prop].get('location', {}).get('file')
    prop_line = lambda prop: properties[prop].get('location', {}).get('line')

    lines = [(prop_file(prop), int(prop_line(prop))) for prop in props]
    return sorted(set(lines))


def failure_loop_name(failure):
    parts = failure.split('.')
    if len(parts) == 3 and parts[1] == 'unwind':
        return '{}.{}'.format(parts[0], parts[2])
    return None

def clean_loop_name(failure):
    parts = failure.split('.')
    if len(parts) == 2:
        name, num = parts
        idx = name.find('$')
        name = name if idx < 0 else name[:idx]
        return '{}.{}'.format(name, num)
    return None

def loop_issue_lines(failures, loops):
    loop_names = [failure_loop_name(fail)
                  for fail in failures if failure_loop_name(fail) in loops]

    loop_file = lambda loop: loops[loop].get('file')
    loop_line = lambda loop: loops[loop].get('line')

    lines = [(loop_file(loop), int(loop_line(loop))) for loop in loop_names]
    return sorted(set(lines))

def other_issues_count(failures, properties, loops):
    others = [fail for fail in failures if
              fail not in properties and
              failure_loop_name(fail) and
              failure_loop_name(fail) not in loops]
    return len(others)

################################################################

def missing_functions(viewer_results):
    warnings = viewer_results['warning']
    missing_funcs = [warn[len('**** WARNING: no body for function '):].strip()
                     for warn in warnings
                     if warn.startswith('**** WARNING: no body for function ')]

    return sorted(set(missing_funcs))

################################################################

def proof_summary():
    with open('viewer-results.json') as data:
        viewer_results = json.load(data)
    with open('viewer-coverage.json') as data:
        viewer_coverage = json.load(data)
    with open('viewer-properties.json') as data:
        viewer_properties = json.load(data)
    with open('viewer-loops.json') as data:
        viewer_loops = json.load(data)
    with open('cbmc-viewer.json') as data:
        cbmc_viewer = json.load(data)
        expected_missing = cbmc_viewer.get('expected-missing-functions', [])
        proof_root = cbmc_viewer.get('proof-root')
        proof_name = cbmc_viewer.get('proof-name', 'PROOF')

    failures = viewer_results['result']['false']
    properties = viewer_properties['properties']
    loops = {clean_loop_name(name): data
             for name, data in viewer_loops['loops'].items()}
    missing_funcs = missing_functions(viewer_results)

    return {
        proof_name: {
            'model-lines':
                model_lines(viewer_coverage, proof_root),
            'project-lines':
                project_lines(viewer_coverage, proof_root),
            'project-lines-hit':
                project_lines_hit(viewer_coverage, proof_root),
            'property-issue-lines':
                property_issue_lines(failures, properties),
            'loop-issue-lines':
                loop_issue_lines(failures, loops),
            'other-issues-count':
                other_issues_count(failures, properties, loops),
            'expected-missing-funcs':
                sorted([func for func in missing_funcs
                        if func in expected_missing]),
            'unexpected-missing-funcs':
                sorted([func for func in missing_funcs
                        if func not in expected_missing])
        }
    }

if __name__ == '__main__':
    with open('viewer-summary.json', 'w') as output:
        output.write(json.dumps(proof_summary(), indent=2))
