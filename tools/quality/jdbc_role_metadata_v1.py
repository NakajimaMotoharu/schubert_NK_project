"""Bounded literal source candidates only: no file IO, target execution or authority inference.

This is not a Java parser/type resolver. Callers still bind exact source/hash, diagnostic spans,
catch types, complete scope and manually reviewed purpose. Outputs never authorize a test.
"""
import re

MAXIMUM_SOURCE_CHARACTERS = 1048576
MAXIMUM_ALIAS_CHARACTERS = 8192
_CONDITIONAL = re.compile(
    r'if \(JdbcResourceFailures\.replace\((statementFailure|rowFailure|rowsFailure), '
    r'([A-Za-z_][A-Za-z_0-9]*)\)\) throw \2;')
_ALIAS = re.compile(r'var ([A-Za-z_][A-Za-z_0-9]*) = present\((statement|rows)\);')


def _require(ok, message):
    if not ok:
        raise ValueError(message)


def close_conditions(source):
    """Return immutable (primary, cleanup, start, end) candidates; no AST/semantic claim."""
    _require(type(source) is str, 'ordinary source text required')
    _require(len(source) <= MAXIMUM_SOURCE_CHARACTERS, 'bounded source text required')
    _require('\r' not in source and '\0' not in source and '\\u' not in source,
             'unambiguous ordinary LF source required')
    return tuple((match.group(1), match.group(2), match.start(), match.end())
                 for match in _CONDITIONAL.finditer(source))


def alias_variable(line, resource):
    """Bind the literal declared symbol to one closed borrowed-resource name."""
    _require(type(line) is str and type(resource) is str, 'literal alias and resource required')
    _require(resource in ('statement', 'rows'), 'closed resource name required')
    _require(len(line) <= MAXIMUM_ALIAS_CHARACTERS, 'bounded alias line required')
    _require('\r' not in line and '\0' not in line and '\\u' not in line
             and '\n' not in line.removesuffix('\n'), 'one ordinary physical line required')
    found = _ALIAS.fullmatch(line.strip())
    _require(found is not None, 'literal identity alias declaration required')
    _require(found.group(2) == resource, 'same resource argument required')
    return found.group(1)
