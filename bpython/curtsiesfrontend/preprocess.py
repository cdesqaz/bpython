"""Tools for preparing code to be run in the REPL (removing blank lines,
etc)"""

from ..lazyre import LazyReCompile
from itertools import tee, islice, chain

# TODO specifically catch IndentationErrors instead of any syntax errors

indent_empty_lines_re = LazyReCompile(r"\s*")
tabs_to_spaces_re = LazyReCompile(r"^\t+")


def indent_empty_lines(s, compiler):
    """Indents blank lines that would otherwise cause early compilation

    Only really works if starting on a new line"""
    lines = s.split("\n")
    ends_with_newline = False
    if lines and not lines[-1]:
        ends_with_newline = True
        lines.pop()
    result_lines = []

    prevs, lines, nexts = tee(lines, 3)
    prevs = chain(("",), prevs)
    nexts = chain(islice(nexts, 1, None), ("",))

    for p_line, line, n_line in zip(prevs, lines, nexts):
        if len(line) == 0:
            p_indent = indent_empty_lines_re.match(p_line).group()
            n_indent = indent_empty_lines_re.match(n_line).group()
            result_lines.append(min([p_indent, n_indent], key=len) + line)
        else:
            result_lines.append(line)

    return "\n".join(result_lines) + ("\n" if ends_with_newline else "")


def leading_tabs_to_spaces(s):
    lines = s.split("\n")
    result_lines = []

    def tab_to_space(m):
        return len(m.group()) * 4 * " "

    for line in lines:
        result_lines.append(tabs_to_spaces_re.sub(tab_to_space, line))
    return "\n".join(result_lines)


def preprocess(s, compiler):
    return indent_empty_lines(leading_tabs_to_spaces(s), compiler)
