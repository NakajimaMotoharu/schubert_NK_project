"""Literal current prior-run fixture guards; no operations or production expected generator."""
def prior_history(rows, day):
    if type(rows) is not list or len(rows) != 472 or type(day) is not str: return False
    if any(type(r) is not dict or not {'business_date', 'run_id', 'status'} <= set(r) for r in rows): return False
    today = [r for r in rows if r['business_date'] == day]
    return len(today) == 10 and {r['run_id'] for r in today} == {'b7e73994-b951-4696-bdd1-cfbc8a10e734'} and all(r['status'] == 'SUCCESS' for r in today)


def empty_oracle(low, high):
    return type(low) is dict and type(high) is dict and bool(low) and low == high and all(type(v) is list and v == [] for v in low.values())
