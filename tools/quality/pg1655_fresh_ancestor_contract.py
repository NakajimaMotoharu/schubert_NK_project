"""SSC273 independent current actor comparison; only two shared chrono fields.

Old records are untouched. A fresh full image is required for every later
pidfd/reservation check; this function grants no syscall or signal capability.
"""


def validate_actor(old, fresh, upper_ns):
    keys = {'pid', 'ticks', 'argvSha256', 'authority', 'cgroup', 'fds'}
    if type(old) is not dict or type(fresh) is not dict or set(old) != keys or set(fresh) != keys or type(upper_ns) is not int or upper_ns < 0:
        raise ValueError('complete typed old/fresh actor required')
    if any(old[k] != fresh[k] for k in keys - {'fds'}):
        raise ValueError('fixed actor identity/authority required')
    if type(old['fds']) is not dict or type(fresh['fds']) is not dict or old['fds'].keys() != fresh['fds'].keys() or len(old['fds']) != 97:
        raise ValueError('all97 fixed FD identities required')
    for name in old['fds']:
        a, b = old['fds'][name], fresh['fds'][name]
        if type(a) is not dict or type(b) is not dict or set(a) != {'metadata', 'target'} or set(b) != set(a) or a['target'] != b['target']:
            raise ValueError('fixed fd targets required')
        for value in [a['metadata'], b['metadata']]:
            if type(value) is not list or len(value) != 9 or any(type(v) is not int or v < 0 for v in value):
                raise ValueError('complete typed FD metadata required')
        if name in ['29', '32']:
            if a['target'] != '/run' or a['metadata'][:7] != b['metadata'][:7] or any(not a['metadata'][i] <= b['metadata'][i] <= upper_ns for i in [7, 8]):
                raise ValueError('current shared ancestor guard/chrono required')
        elif a != b:
            raise ValueError('all other95 FD metadata unchanged required')
    if not {'29', '32'} <= old['fds'].keys() or fresh['fds']['29'] != fresh['fds']['32']:
        raise ValueError('same linked shared /run object required')
    return True


def same_fresh(expected, actual):
    if type(expected) is not dict or type(actual) is not dict or expected != actual:
        raise ValueError('same complete fresh image required')
    return True
