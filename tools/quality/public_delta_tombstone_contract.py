"""Explicit deleted Git text scope only; unknown/missing current data never becomes clean."""


def verify_scope(declared, observed):
    if (not isinstance(declared, (set, frozenset)) or not declared or declared != observed
        or any(not isinstance(path, str) or not path.startswith('src/') or '..' in path.split('/')
               or '/private' in path or not path.endswith('.java') for path in declared)):
        raise ValueError('exact declared public Java tombstones must equal actual Git deletions')


def verify_blob(mode, kind, size):
    if mode not in ('100644', '100755') or kind != 'blob' or not (0 < size <= 2 * 1024 * 1024):
        raise ValueError('bounded original regular tracked text blob required')
