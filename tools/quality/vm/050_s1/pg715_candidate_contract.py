"""Only Expiry outer byte change and two internal classes; no operation authority."""
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
CHANGED = {'batch': frozenset({'dev/codex/schubert/nk/batch/file/CleanupExpiryExecution.class'})}
ADDED = {'batch': frozenset({'dev/codex/schubert/nk/batch/file/CleanupExpiryExecution$1.class',
                           'dev/codex/schubert/nk/batch/file/CleanupExpiryExecution$ExpiryWork.class'})}


def verify_delta(old, candidate):
    if type(old) is not dict or type(candidate) is not dict or set(old) != set(MODULES) or set(candidate) != set(MODULES):
        raise ValueError('candidate module inventory')
    count = 0
    for module in MODULES:
        before, after = old[module], candidate[module]
        if type(before) is not dict or type(after) is not dict or not before or before.keys()-after.keys():
            raise ValueError('candidate class inventory')
        for rows in (before, after):
            if any(type(n) is not str or not n.endswith('.class') or type(h) is not str or len(h) != 64 or set(h)-set('0123456789abcdef') for n, h in rows.items()):
                raise ValueError('candidate class digest')
        if {n for n in before if before[n] != after[n]} != CHANGED.get(module, frozenset()) or after.keys()-before.keys() != ADDED.get(module, frozenset()):
            raise ValueError('candidate class delta')
        count += len(after)
    return count
