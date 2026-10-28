"""Exact token inverse for ten private field renames and one fixture literal extraction."""
from public_java_digest_provenance import LEX

def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(old,new,transfer):
    baseline = tokens(old); current = tokens(new)
    assert 'OBSERVED_AT' not in baseline and baseline.count('AT') >= 2
    assert current.count('OBSERVED_AT') == baseline.count('AT') and 'AT' not in current
    assert current.count('at') == baseline.count('at')
    if transfer:
        declaration = tokens('private static final String DEBUG_MODE_FIXTURE = "DEBUG";')
        hits = [i for i in range(len(current)) if current[i:i+len(declaration)] == declaration]
        assert len(hits) == 1 and baseline.count('"DEBUG"') == 11
        i = hits[0];del current[i:i+len(declaration)]
        assert current.count('DEBUG_MODE_FIXTURE') == 11 and '"DEBUG"' not in current
        current = ['"DEBUG"' if value == 'DEBUG_MODE_FIXTURE' else value for value in current]
    else:
        assert 'DEBUG_MODE_FIXTURE' not in current
    restored = ['AT' if value == 'OBSERVED_AT' else value for value in current]
    assert restored == baseline
    return dict(originalTokens=len(baseline),fieldReferences=baseline.count('AT'),factoryTokens=baseline.count('at'),debugLiterals=11 if transfer else 0)

def negative(old,new,transfer):
    variants = [new.replace('OBSERVED_AT','OTHER_AT',1),new.replace(' at(',' wrongAt(',1),new.replace('assertTrue(','assertFalse(',1),new.replace('2026-10-','2025-10-',1),new.rstrip()[:-1]]
    if transfer:
        variants.extend([new.replace('String DEBUG_MODE_FIXTURE = "DEBUG"','String DEBUG_MODE_FIXTURE = "STANDARD"',1),new.replace('"debug"','"DEBUG"',1)])
    for value in variants:
        assert value != new
        try: inverse(old,value,transfer)
        except AssertionError: pass
        else: raise AssertionError('non-equivalent source mutation accepted')
    return len(variants)
