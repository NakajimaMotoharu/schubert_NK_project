"""Tool-only bounded PMD span contract: LF source, ASCII/tab-free boundary prefixes, exclusive end."""
import re

FIELDS = ('beginline', 'begincolumn', 'endline', 'endcolumn')

def span(text, attributes):
    if not isinstance(text, str) or not isinstance(attributes, dict) or '\r' in text or '\0' in text or '\\u' in text:
        raise ValueError('ordinary LF source without unresolved Unicode escapes required')
    values = []
    for key in FIELDS:
        value = attributes.get(key)
        if not isinstance(value, str) or re.fullmatch(r'[1-9][0-9]*', value) is None:
            raise ValueError('positive decimal one-origin coordinates required')
        values.append(int(value))
    begin_line, begin_column, end_line, end_column = values
    lines = text.splitlines(keepends=True)
    if not 1 <= begin_line <= end_line <= len(lines):
        raise ValueError('source line range required')
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1]+len(line))
    points = []
    for number, column in [(begin_line, begin_column), (end_line, end_column)]:
        line = lines[number-1].removesuffix('\n')
        index = column-1
        if not 0 <= index <= len(line) or not line[:index].isascii() or '\t' in line[:index]:
            raise ValueError('unambiguous ASCII boundary prefix and in-line column required')
        points.append(offsets[number-1]+index)
    start, end = points
    if start >= end:
        raise ValueError('nonempty half-open diagnostic span required')
    return start, end, text[start:end]

def selftest():
    def coordinates(a, b, c, d):
        return dict(zip(FIELDS, map(str, (a, b, c, d))))
    positives = [
        ('alpha beta\nzeta\n', coordinates(1,7,1,11), (6,10,'beta')),
        ('alpha beta\nzeta\n', coordinates(1,7,2,5), (6,15,'beta\nzeta')),
        ('one', coordinates(1,1,1,4), (0,3,'one')),
        ('  statement = db;\n', coordinates(1,3,1,12), (2,11,'statement')),
    ]
    for text, attributes, expected in positives:
        assert span(text, attributes) == expected
    original = coordinates(1,1,1,4)
    negatives = []
    for key, value in [('beginline','0'),('begincolumn','0'),('endline','2'),('endcolumn','5'),
                       ('beginline',True),('endcolumn',4),('begincolumn','+1'),('endcolumn',' 4')]:
        bad = dict(original)
        bad[key] = value
        negatives.append(('one', bad))
    negatives += [('one',coordinates(1,4,1,1)),('one',coordinates(1,2,1,2)),
        ('one',{}),('one\r\n',original),('one\0',original),('\\u0061',original),
        ('\tone',coordinates(1,2,1,5)),('éone',coordinates(1,2,1,5)),
        (None,original),('one',None)]
    for text, attributes in negatives:
        try:
            span(text, attributes)
        except ValueError:
            pass
        else:
            raise AssertionError('ambiguous or malformed PMD span accepted')
    assert len(negatives) == 18
    return dict(positive=4, negative=18, productTestsExecuted=0, convention='PMD_1_ORIGIN_EXCLUSIVE_END_TO_PYTHON_HALF_OPEN')
