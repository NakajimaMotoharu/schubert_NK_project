"""SSC274 pure guards; no process, DB or signal operations."""


def fresh_parent(old, actual, upper_ns):
    keys = {'pid', 'ticks', 'argvSha256', 'authority', 'cgroup', 'fds'}
    if type(old) is not dict or type(actual) is not dict or set(old) != keys or set(actual) != keys or type(upper_ns) is not int or upper_ns < 0:
        raise ValueError('complete typed parent required')
    if any(old[k] != actual[k] for k in keys - {'fds'}):
        raise ValueError('same parent authority required')
    if type(old['fds']) is not dict or type(actual['fds']) is not dict or set(old['fds']) != set(actual['fds']) or len(old['fds']) != 101:
        raise ValueError('all101 FD identities required')
    for name, a in old['fds'].items():
        b = actual['fds'][name]
        if type(a) is not dict or type(b) is not dict or set(a) != {'metadata', 'target'} or set(b) != set(a) or type(a['target']) is not str or a['target'] != b['target']:
            raise ValueError('fixed complete FD target required')
        for value in [a['metadata'], b['metadata']]:
            if type(value) is not list or len(value) != 9 or any(type(x) is not int or x < 0 for x in value):
                raise ValueError('typed complete FD metadata required')
        if name in ['29', '32']:
            if a['target'] != '/run' or a['metadata'][:7] != b['metadata'][:7] or any(not a['metadata'][i] <= b['metadata'][i] <= upper_ns for i in [7, 8]):
                raise ValueError('fresh shared ancestor chrono and guard required')
        elif a != b:
            raise ValueError('all other99 FD attributes unchanged required')
    if not {'29', '32'} <= set(old['fds']) or actual['fds']['29'] != actual['fds']['32']:
        raise ValueError('same linked run object required')
    return True


def parent_after_ref(before, actual, pipes):
    if type(before) is not dict or type(actual) is not dict or set(actual) != set(before) or type(pipes) is not set or len(pipes) != 2 or any(type(p) is not str or not p.startswith('pipe:[') for p in pipes):
        raise ValueError('fixed before/current and two child pipes required')
    if any(before[k] != actual[k] for k in set(before) - {'fds'}):
        raise ValueError('same remaining parent required')
    a, b = before['fds'], actual['fds']
    if type(a) is not dict or type(b) is not dict or not set(b) <= set(a) or any(a[k] != b[k] for k in b):
        raise ValueError('no new/reused/changed remaining FD required')
    if any(a[k]['target'] not in pipes for k in set(a) - set(b)):
        raise ValueError('only known child stdin/stdout pipe FDs may disappear')
    return True
