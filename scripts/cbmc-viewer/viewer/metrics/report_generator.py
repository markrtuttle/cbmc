#!/usr/bin/env python3
"""
Generate a summary.json for the whole project.
"""

import os                                 # get unix
import json
from   glob    import glob                # file name expansion
import pandas as pd

def chartGenerator():
    root = os.getcwd()
    report = {"Proof":{}, "Model LOC":{}, "Project LOC":{}, "Project Coverage":{}, "Property Issues":{}, "Loop Issues":{}, "Other Issues":{}, "SAT Variables":{}, "SAT Clauses":{}, "SAT Time":{}}

    for harness in glob(root + '/*'):      # for all harnesses
        if (os.path.isdir(harness)):
            with open(harness + '/viewer-summary.json', 'r') as f:
                viewer_summary = f.read()
            viewer_dict = json.loads(viewer_summary)
            report['Proof'][os.path.basename(harness)] = os.path.basename(harness)
            report['Model LOC'][os.path.basename(harness)] = len(viewer_dict[os.path.basename(harness)]['model-lines'])
            report['Project LOC'][os.path.basename(harness)] = len(viewer_dict[os.path.basename(harness)]['project-lines'])
            report['Project Coverage'][os.path.basename(harness)] = round(float(len(viewer_dict[os.path.basename(harness)]['project-lines-hit']))/float(len(viewer_dict[os.path.basename(harness)]['project-lines'])), 2)
            report['Property Issues'][os.path.basename(harness)] = len(viewer_dict[os.path.basename(harness)]['property-issue-lines'])
            report['Loop Issues'][os.path.basename(harness)] = len(viewer_dict[os.path.basename(harness)]['loop-issue-lines'])
            report['Other Issues'][os.path.basename(harness)] = viewer_dict[os.path.basename(harness)]['other-issues-count']

    with open('summary.json', 'r') as f:
        viewer_summary = f.read()
    summary = json.loads(viewer_summary)

    report['Proof']['TOTAL'] = "TOTAL"
    report['Model LOC']['TOTAL'] = len(summary['summary']['model-lines'])
    report['Project LOC']['TOTAL'] = len(summary['summary']['project-lines'])
    report['Project Coverage']['TOTAL'] = round(float(len(summary['summary']['project-lines-hit']))/float(len(summary['summary']['project-lines'])), 2)
    report['Property Issues']['TOTAL'] = len(summary['summary']['property-issue-lines'])
    report['Loop Issues']['TOTAL'] = len(summary['summary']['loop-issue-lines'])
    report['Other Issues']['TOTAL'] = summary['summary']['other-issues-count']

    with open('report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    df = pd.read_json (r'report.json')
    df.to_csv (r'report.csv', index = None)

def summaryGenerator():
    root = os.getcwd()
    summary = {"summary": {}}

    for harness in glob(root + '/*'):      # for all harnesses
        if (os.path.isdir(harness)):
            with open(harness + '/viewer-summary.json', 'r') as f:
                viewer_summary = f.read()
            viewer_dict = json.loads(viewer_summary)
            if len(summary['summary']) == 0:
                summary['summary']['model-lines'] = viewer_dict[os.path.basename(harness)]['model-lines']
                summary['summary']['project-lines'] = viewer_dict[os.path.basename(harness)]['project-lines']
                summary['summary']['project-lines-hit'] = viewer_dict[os.path.basename(harness)]['project-lines-hit']
                summary['summary']['property-issue-lines'] = viewer_dict[os.path.basename(harness)]['property-issue-lines']
                summary['summary']['loop-issue-lines'] = viewer_dict[os.path.basename(harness)]['loop-issue-lines']
                summary['summary']['other-issues-count'] = viewer_dict[os.path.basename(harness)]['other-issues-count']
                summary['summary']['expected-missing-funcs'] = viewer_dict[os.path.basename(harness)]['expected-missing-funcs']
                summary['summary']['unexpected-missing-funcs'] = viewer_dict[os.path.basename(harness)]['unexpected-missing-funcs']
            else:
                summary['summary']['model-lines'] += viewer_dict[os.path.basename(harness)]['model-lines']
                summary['summary']['project-lines'] += viewer_dict[os.path.basename(harness)]['project-lines']
                summary['summary']['project-lines-hit'] += viewer_dict[os.path.basename(harness)]['project-lines-hit']
                summary['summary']['property-issue-lines'] += viewer_dict[os.path.basename(harness)]['property-issue-lines']
                summary['summary']['loop-issue-lines'] += viewer_dict[os.path.basename(harness)]['loop-issue-lines']
                summary['summary']['other-issues-count'] += viewer_dict[os.path.basename(harness)]['other-issues-count']
                summary['summary']['expected-missing-funcs'] += viewer_dict[os.path.basename(harness)]['expected-missing-funcs']
                summary['summary']['unexpected-missing-funcs'] += viewer_dict[os.path.basename(harness)]['unexpected-missing-funcs']



    with open('summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)

def main():
    summaryGenerator()
    chartGenerator()

if __name__ == '__main__':
    main()
