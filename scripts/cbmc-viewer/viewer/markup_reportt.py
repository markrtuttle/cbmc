import os

import markupt

def functions_by_decreasing_coverage(coverage):
    data = [(fyle, func, func_coverage)
            for fyle, fyle_coverage in coverage.function_summary.items()
            for func, func_coverage in fyle_coverage.items()]
    return sorted(data,
                  key=lambda tup: (-tup[2]['percentage'], tup[0], tup[1]))

def coverage_detail(coverage, symbols):
    """Detailed coverage report."""

    report = []
    report.append('<table class="coverage">')
    report.append('<tr>'
                  '<th class="coverage">Coverage</th>'
                  '<th class="function">Function</th>'
                  '<th class="file">File</th>'
                  '</tr>')

    for fyle, func, cov in functions_by_decreasing_coverage(coverage):
        report.append('<tr>'
                      '<td class="coverage">{:.2f} ({}/{})</td>'
                      '<td class="function">{}</td>'
                      '<td class="file">{}</td>'
                      '</tr>'
                      .format(cov['percentage'], cov['hit'], cov['total'],
                              markupt.link_text_to_symbol(func, func, symbols),
                              markupt.link_text_to_file(fyle, fyle)))

    report.append("</table>")
    return '\n'.join(report)

def coverage_summary(coverage):
    """Summary coverage report."""

    return ('<p>Coverage: {:.2f} (reached {} of {} reachable lines)</p>'
            .format(coverage.summary['percentage'],
                    coverage.summary['hit'],
                    coverage.summary['total']))

################################################################

def assemble_results(results, properties, loops):
    def tree_insert(tree, path, func, line, result, desc):
        tree[path] = tree.get(path, {})
        tree[path][func] = tree[path].get(func, {})
        tree[path][func][line] = tree[path][func].get(line) or set()
        tree[path][func][line].add((result, desc))
        return tree

    prop_failure = {}
    loop_failure = {}
    unknown_failure = []

    for result in results.results[False]:
        prop = properties.properties.get(result)
        if not prop:

            # the result is a loop unwinding failure
            loop = result.replace('.unwind.', '.')
            if loop in loops.names():
                path, func, line = loops.lookup(loop)
                loop_failure = tree_insert(loop_failure,
                                           path, func, line,
                                           result, result)
                continue

            # the result is an unknown property failure
            unknown_failure.append(result)
            continue

        # the result is an ordinary property failure
        desc = prop['description']
        srcloc = prop['location']
        path = srcloc['file']
        func = srcloc['function']
        line = srcloc['line']
        prop_failure = tree_insert(prop_failure, path, func, line, result, desc)

    return prop_failure, loop_failure, unknown_failure

def failure_summary(failures, symbols):
    if not failures:
        return None

    report = []
    report.append('<ul>')

    for path, path_results in failures.items():
        report.append('<li class="file">File {}'
                      '<ul>'
                      .format(markupt.link_text_to_file(path, path)))
        for func, func_results in path_results.items():
            report.append('<li class="function">Function {}'
                          '<ul>'
                          .format(markupt.link_text_to_symbol(
                              func, func, symbols)))
            for line, line_results in func_results.items():
                report.append('<li class="line">Line {}'
                              '<ul>'
                              .format(markupt.link_text_to_line(
                                  line, path, line)))
                for name, desc in sorted(line_results):
                    report.append('<li> '
                                  '[<a href="traces/{}.html">trace</a>] {}'
                                  .format(name, desc))
                report.append('</ul>')
            report.append('</ul>')
        report.append('</ul>')
    report.append('</ul>')

    return '\n'.join(report)

def compact_failure_summary(failures, link_loop=False):
    if not failures:
        return None

    report = []
    report.append('<ul>')

    for path, path_results in failures.items():
        for _, func_results in path_results.items():
            for line, line_results in func_results.items():
                for name, desc in sorted(line_results):

                    if link_loop and not path.startswith('<'):
                        desc = '<a href="{}.html#{}">{}</a>'.format(
                            path, line, desc
                        )

                    item = []
                    item.append('<li> [<a href="traces/{}.html">trace</a>] {}'
                                .format(name, desc))
                    item.append('in line {}'.format(
                        markupt.link_text_to_line(line, path, line)
                    ))
                    item.append('in file {}'.format(
                        markupt.link_text_to_file(path, path)
                    ))
                    report.append(' '.join(item))

    report.append('</ul>')
    return '\n'.join(report)

def result_summary(results, properties, loops, symbols):
    (prop, loop, unknown) = assemble_results(results, properties, loops)
    loop_summary = compact_failure_summary(loop, True)
    unknown_summary = compact_failure_summary(unknown)
    prop_summary = failure_summary(prop, symbols)

    if not loop_summary and not unknown_summary and not prop_summary:
        return '<p>None</p>'

    report = []
    if loop_summary:
        report.append('<ul><li>Loop unwinding failures</li>')
        report.append(loop_summary)
        report.append('</ul>')

    if unknown_summary:
        report.append('<ul><li>Unknown failures</li>')
        report.append(unknown_summary)
        report.append('</ul>')

    if prop_summary:
        report.append(prop_summary)

    return '\n'.join(report)

################################################################

def missing_functions_section(functions, config):
    """Report on functions omitted from the test."""

    functions = sorted(functions)
    if not functions:
        return ""

    section = []

    expected_missing_functions = config.expected_missing_functions()
    if expected_missing_functions is None:
        section.append("<p>Functions omitted from test:</p><ul>")
        section.extend(["<li>{}</li>".format(func) for func in functions])
        section.append("</ul>")
        return '\n'.join(section)

    expected = [func for func in functions
                if func in expected_missing_functions]
    unexpected = [func for func in functions
                  if func not in expected_missing_functions]

    if expected:
        section.append("<p>Functions omitted from test (expected):</p><ul>")
        section.extend(["<li>{}</li>".format(func) for func in expected])
        section.append("</ul>")
    if unexpected:
        section.append("<p>Functions omitted from test (unexpected):</p><ul>")
        section.extend(["<li>{}</li>".format(func) for func in unexpected])
        section.append("</ul>")
    return '\n'.join(section)

def warning_section(results, config):
    """Report on warnings issued by CBMC."""

    warnings = results.warning
    if not warnings:
        return "<p>None</p>"

    prefix = "**** WARNING:"
    length = len(prefix)
    warnings = [warning[length:].strip() for warning in warnings]

    prefix = "no body for function"
    length = len(prefix)
    function_warnings = [warning.strip()
                         for warning in warnings
                         if warning.startswith(prefix)]
    other_warnings = [warning.strip()
                      for warning in warnings
                      if not warning.startswith(prefix)]

    functions = [warning[length:].strip() for warning in function_warnings]

    section = []
    section.append(missing_functions_section(functions, config))
    if other_warnings:
        section.append("<p>Warnings:</p><ul>")
        section.extend(["<li>{}</li>".format(warn)
                        for warn in sorted(other_warnings)])
        section.append("</ul>")
    return '\n'.join(section)

################################################################

def format_report(coverage, symbols, results, properties, loops, config, htmldir='html'):
    with open(os.path.join(htmldir, 'index.html'), 'w') as html:
        html.write(
            HTML.format(
                title="CBMC",
                root=".",
                coverage_summary=coverage_summary(coverage),
                coverage_detail=coverage_detail(coverage, symbols),
                error_report=result_summary(results, properties, loops, symbols),
                warnings_report=warning_section(results, config)
            )
        )


HTML = """
<html>
<head>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="{root}/viewer.css">
</head>

<body>
<h1>
CBMC report
</h1>
<div class="coverage">
<h2>Coverage</h2>
{coverage_summary}
{coverage_detail}
</div>
<div class="warnings">
<h2> Warnings</h2>
{warnings_report}
</div>
<div class="errors">

<h2>Errors</h2>
{error_report}
</div>
</body>
</html>
"""
