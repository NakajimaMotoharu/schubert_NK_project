"""Preserve all original codec cases; allow exactly the manually reviewed ceiling method."""
import hashlib
from public_java_digest_provenance import LEX

NAME = 'numericSemanticCeilingIsIndependentOfWireAndLongCapacity'
BODY_SHA = '5514c99f6e498fcbf14d905f963c987658f9e1f6e5d88193feb5030f6d0594e6'

def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(old,new):
    a,b = tokens(old),tokens(new)
    assert NAME not in a and b.count(NAME) == 1
    start = b.index(NAME)-3;assert b[start:start+7] == ['@','Test','void',NAME,'(',')','{']
    end = start+7;depth = 1
    while depth:
        depth += (b[end] == '{')-(b[end] == '}');end += 1
    assert hashlib.sha256('\n'.join(b[start:end]).encode()).hexdigest() == BODY_SHA
    assert b[:start]+b[end:] == a
    return dict(originalTokens=len(a),addedMethodTokens=end-start,addedMethods=1,originalFiveCasesUnchanged=True,newMethodTokenSha256=BODY_SHA)

def negatives(old,new):
    values = [new.replace('"AB"','"AC"',1),new.replace('9_223_372_036_854_775_806L','9_223_372_036_854_775_805L',1),
        new.replace('"000100"','"000099"',1),new.replace('assertEquals(Long.MAX_VALUE,','assertEquals(0,',1),
        new.replace('semanticMaximum));','Long.MAX_VALUE));',1),new.replace('@Test','',1)]
    for value in values:
        assert value != new
        try:inverse(old,value)
        except (AssertionError,IndexError,ValueError):pass
        else:raise AssertionError('changed old oracle or weakened new ceiling fixture accepted')
    return len(values)

def numeric_fixture():
    rows = [('000099',99,99),('000100',99,None),('9223372036854775806',9223372036854775806,9223372036854775806),
        ('9223372036854775807',9223372036854775807,9223372036854775807),('9223372036854775807',9223372036854775806,None)]
    for wire,maximum,expected in rows:
        value = int(wire);assert wire.isascii() and wire.isdecimal() and 0 <= value <= (1<<63)-1
        assert (value <= maximum) == (expected is not None)
        if expected is not None:assert value == expected
    return rows
