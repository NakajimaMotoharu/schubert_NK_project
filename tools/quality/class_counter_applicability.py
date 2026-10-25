"""Keep zero-counter metadata separate from measured four-counter class qualification."""
KINDS = frozenset(('LINE','METHOD','CLASS','BRANCH'))


def classify(counters):
    if not isinstance(counters,dict) or set(counters) != KINDS:
        raise ValueError('four exact counter kinds required')
    for value in counters.values():
        if not isinstance(value,dict) or set(value) != {'missed','covered'}:
            raise ValueError('exact missed/covered required')
        if any(type(n) is not int or n < 0 for n in value.values()):
            raise ValueError('nonnegative integer counters required')
    totals = {kind:v['missed'] + v['covered'] for kind,v in counters.items()}
    if not any(totals.values()):
        return 'NO_COUNTERS_NOT_A_MEASURED_PASS'
    if any(totals[k] == 0 for k in ('LINE','METHOD','CLASS')):
        return 'INCOMPLETE_APPLICABILITY_NOT_A_MEASURED_PASS'
    if any(v['missed'] for v in counters.values()):
        return 'MISSED_COUNTERS'
    return 'FOUR100_MEASURED_APPLICABLE'
