"""PG-D395/396 closed candidate byte delta. Data validation, no deployment authority."""
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
PREFIX = 'dev/codex/schubert/nk/bootstrap/'
CHANGED = frozenset(PREFIX + name + '.class' for name in (
    'FixedNativeCoverageCheckpoint', 'FixedNativeCoverageCheckpoint$PublicAgent',
    'NativeCoveragePrivateFile'))
ADDED = frozenset(PREFIX + 'FixedNativeCoverageCheckpoint$PublicAgent$' + name + '.class'
                  for name in ('Classes', 'Sources', 'Invocation'))


def verify_delta(old, candidate):
    if not isinstance(old, dict) or not isinstance(candidate, dict):
        raise ValueError('candidate module inventory')
    if set(old) != set(MODULES) or set(candidate) != set(MODULES):
        raise ValueError('candidate module inventory')
    count = 0
    for module in MODULES:
        before, after = old[module], candidate[module]
        if not isinstance(before, dict) or not isinstance(after, dict) or not before:
            raise ValueError('candidate class inventory')
        for rows in (before, after):
            if any(not isinstance(n, str) or not n.endswith('.class')
                   or not isinstance(h, str) or len(h) != 64
                   or set(h) - set('0123456789abcdef') for n, h in rows.items()):
                raise ValueError('candidate class digest')
        removed = set(before) - set(after)
        added = set(after) - set(before)
        changed = {n for n in set(before) & set(after) if before[n] != after[n]}
        if removed or added != (ADDED if module == 'bootstrap' else set()) \
                or changed != (CHANGED if module == 'bootstrap' else set()):
            raise ValueError('candidate class delta')
        count += len(after)
    return count
