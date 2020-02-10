#!/usr/bin/env python3
"""
Generate a summary.json for the whole project.
"""

import collections
import os                                 # get unix
import json
from   glob    import glob                # file name expansion
import pandas as pd
import logging                            # setup log files

def chartGenerator():
    root = os.getcwd()
    report = collections.OrderedDict()

    def empty(report, proof):
        report[proof] = collections.OrderedDict()
        report[proof]['Proof'] = proof
        report[proof]['Model LOC'] = ""
        report[proof]['Project LOC'] = ""
        report[proof]['Project Coverage'] = ""
        report[proof]['Property Issues'] = ""
        report[proof]['Loop Issues'] = ""
        report[proof]['Other Issues'] = ""
        report[proof]['Expected Missing Functions'] = ""
        report[proof]['Unexpected Missing Functions'] = ""
        report[proof]['SAT Variables'] = ""
        report[proof]['SAT Clauses'] = ""
        report[proof]['SAT Time'] = ""
        return report


    for harness in glob(root + '/*'):      # for all harnesses
        if (os.path.isdir(harness)):
            try:
                with open(harness + '/viewer-summary.json', 'r') as f:
                    viewer_summary = f.read()
                viewer_dict = json.loads(viewer_summary)
                proof = os.path.basename(harness)
                report[proof] = collections.OrderedDict()
                report[proof]['Proof'] = proof
                report[proof]['Model LOC'] = len(viewer_dict[proof]['model-lines'])
                report[proof]['Project LOC'] = len(viewer_dict[proof]['project-lines'])
                try:
                    report[proof]['Project Coverage'] = round(float(len(viewer_dict[proof]['project-lines-hit']))/float(len(viewer_dict[proof]['project-lines'])), 2)
                except ZeroDivisionError:
                    report[proof]['Project Coverage'] = 0
                report[proof]['Property Issues'] = len(viewer_dict[proof]['property-issue-lines'])
                report[proof]['Loop Issues'] = len(viewer_dict[proof]['loop-issue-lines'])
                report[proof]['Other Issues'] = viewer_dict[proof]['other-issues-count']
                report[proof]['Expected Missing Functions'] = len(viewer_dict[proof]['expected-missing-funcs'])
                report[proof]['Unexpected Missing Functions'] = len(viewer_dict[proof]['unexpected-missing-funcs'])
                report[proof]['SAT Variables'] = viewer_dict[proof]['sat-variables']
                report[proof]['SAT Clauses'] = viewer_dict[proof]['sat-clauses']
                report[proof]['SAT Time'] = str(round(float(viewer_dict[proof]['sat-time']), 5))
            except IOError:
                proof = os.path.basename(harness)
                report = empty(report, proof)
                logging.warning(proof + ' does not have a viewer-summary.json file.')
            except json.decoder.JSONDecodeError:
                proof = os.path.basename(harness)
                report = empty(report, proof)
                logging.warning(proof + '/viewer-summary.json is not a parsable json file.')

    with open('summary.json', 'r') as f:
        viewer_summary = f.read()
    summary = json.loads(viewer_summary)

    report['TOTAL'] = collections.OrderedDict()
    report['TOTAL']['Proof'] = "TOTAL"
    report['TOTAL']['Model LOC'] = len(summary['summary']['model-lines'])
    report['TOTAL']['Project LOC'] = len(summary['summary']['project-lines'])
    report['TOTAL']['Project Coverage'] = round(float(len(summary['summary']['project-lines-hit']))/float(len(summary['summary']['project-lines'])), 2)
    report['TOTAL']['Property Issues'] = len(summary['summary']['property-issue-lines'])
    report['TOTAL']['Loop Issues'] = len(summary['summary']['loop-issue-lines'])
    report['TOTAL']['Other Issues'] = summary['summary']['other-issues-count']
    report['TOTAL']['Expected Missing Functions'] = len(summary['summary']['expected-missing-funcs'])
    report['TOTAL']['Unexpected Missing Functions'] = len(summary['summary']['unexpected-missing-funcs'])
    report['TOTAL']['SAT Variables'] = "--"
    report['TOTAL']['SAT Clauses'] = "--"
    report['TOTAL']['SAT Time'] = "--"

    with open('report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    chart = []
    chart.append([
        'Proof',
        'Model LOC',
        'Project LOC',
        'Project Coverage',
        'Property Issues',
        'Loop Issues',
        'Other Issues',
        'Expected Missing Functions',
        'Unexpected Missing Functions',
        'SAT Variables',
        'SAT Clauses',
        'SAT Time'
    ])

    for proof, row in report.items():
        chart.append([row[key] for key in row])

    import csv
    with open('report.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for row in chart:
            writer.writerow(row)

def summaryGenerator():
    root = os.getcwd()
    summary = {"summary": {}}

    for harness in glob(root + '/*'):      # for all harnesses
        if (os.path.isdir(harness)):
            try:
                with open(harness + '/viewer-summary.json', 'r') as f:
                    viewer_summary = f.read()
                viewer_dict = json.loads(viewer_summary)
                proof = os.path.basename(harness)
                if len(summary['summary']) == 0:
                    summary['summary']['model-lines'] = viewer_dict[proof]['model-lines']
                    summary['summary']['project-lines'] = viewer_dict[proof]['project-lines']
                    summary['summary']['project-lines-hit'] = viewer_dict[proof]['project-lines-hit']
                    summary['summary']['property-issue-lines'] = viewer_dict[proof]['property-issue-lines']
                    summary['summary']['loop-issue-lines'] = viewer_dict[proof]['loop-issue-lines']
                    summary['summary']['other-issues-count'] = viewer_dict[proof]['other-issues-count']
                    summary['summary']['expected-missing-funcs'] = viewer_dict[proof]['expected-missing-funcs']
                    summary['summary']['unexpected-missing-funcs'] = viewer_dict[proof]['unexpected-missing-funcs']
                else:
                    summary['summary']['model-lines'] += viewer_dict[proof]['model-lines']
                    summary['summary']['project-lines'] += viewer_dict[proof]['project-lines']
                    summary['summary']['project-lines-hit'] += viewer_dict[proof]['project-lines-hit']
                    summary['summary']['property-issue-lines'] += viewer_dict[proof]['property-issue-lines']
                    summary['summary']['loop-issue-lines'] += viewer_dict[proof]['loop-issue-lines']
                    summary['summary']['other-issues-count'] += viewer_dict[proof]['other-issues-count']
                    summary['summary']['expected-missing-funcs'] += viewer_dict[proof]['expected-missing-funcs']
                    summary['summary']['unexpected-missing-funcs'] += viewer_dict[proof]['unexpected-missing-funcs']
            except IOError:
                proof = os.path.basename(harness)
                logging.warning(proof + ' does not have a viewer-summary.json file.')
            except json.decoder.JSONDecodeError:
                proof = os.path.basename(harness)
                logging.warning(proof + '/viewer-summary.json is not a parsable json file.')

    with open('summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)
    print("Summary generated successfully!")

def main():
    logging.basicConfig(filename='report.log',
                        filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')
    summaryGenerator()
    chartGenerator()

if __name__ == '__main__':
    main()
