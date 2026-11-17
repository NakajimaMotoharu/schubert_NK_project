"""BUG3184/YKT2652: natural NoCode, never missing executable Code, is N/A.

Callers establish no_code from actual JVM Code attributes and bind every physical CRC first.
No file access, exclusions, synthetic filtering, or execution occurs in this pure mapping.
"""

def target_counters(names, classes, no_code, counters):
    if len(names) != len(set(names)):
        raise ValueError('duplicate target')
    result = {}
    for name in names:
        if name not in classes:
            if name not in no_code:
                raise ValueError('missing executable target: ' + name)
            result[name] = {}
        else:
            row = counters(classes[name])
            if name in no_code and any(v['covered'] or v['missed'] for v in row.values()):
                raise ValueError('Code0 contradicts nonzero counters: ' + name)
            result[name] = row
    return result
