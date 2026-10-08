"""SSC230 exact completed runtime635 removal delta, independent literal declaration policy."""
import hashlib
from pg635_resume_contract import MORNING, RUN, NATIVE, TARGET, HISTORY_UNITS, record, fixed_dropin
from pg633_pending_contract import same_value


def require(value):
    if not value:
        raise ValueError('completed runtime635 retirement delta rejected')


def changed_only(before, after, dropin):
    require(type(before) is dict and type(after) is dict and set(before) == set(after)
            and type(dropin) is bytes and type(before['runtime']) is dict and after['runtime'] is None)
    require(before['runtime']['sha256'] == hashlib.sha256(dropin).hexdigest())
    require(same_value(before['runtime'], before['unitFiles'][TARGET])
            and set(before['configuration']) == set(after['configuration']))
    for key in before.keys() - {'configuration', 'runtime', 'unitFiles', 'caddyPre'}:
        require(same_value(before[key], after[key]))
    argv = next(line[10:].decode('ascii') for line in dropin.splitlines()
                if line.startswith(b'ExecStart=') and line != b'ExecStart=')
    require(argv.endswith(' --resume ' + RUN))
    plain = argv.removesuffix(' --resume ' + RUN)
    require(set(after['unitFiles']) == set(before['unitFiles']) - {TARGET}
            and all(same_value(v, before['unitFiles'][p]) for p, v in after['unitFiles'].items()))
    for unit, old in before['configuration'].items():
        new = after['configuration'][unit]; require(set(old) == set(new))
        allowed = {'ExecStart', 'DropInPaths'} if unit == MORNING else {'ExecStart'} if unit in HISTORY_UNITS else set()
        require(all(same_value(old[k], new[k]) for k in old.keys() - allowed))
        a, b = record(old['ExecStart']), record(new['ExecStart'])
        require(a is not None and b is not None)
        if unit == MORNING:
            require(a[:3] == ('/usr/bin/java', argv, 'no') and b[:3] == ('/usr/bin/java', plain, 'no')
                    and b[3:] == ('n/a', 'n/a', '0', '(null)', '0/0')
                    and old['DropInPaths'] == NATIVE + ' ' + TARGET and new['DropInPaths'] == NATIVE)
        elif unit in HISTORY_UNITS:
            require(a[:3] == b[:3] and (old['ExecStart'] == new['ExecStart']
                                      or b[3:] == ('n/a', 'n/a', '0', '(null)', '0/0')))
    a, b = record(before['caddyPre']), record(after['caddyPre'])
    require(a is not None and b is not None and a[:3] == b[:3])
    if before['caddyPre'] != after['caddyPre'] or before['configuration']['caddy.service']['ExecStart'] != after['configuration']['caddy.service']['ExecStart']:
        c = record(after['configuration']['caddy.service']['ExecStart'])
        require(b[3:] == c[3:] == ('n/a', 'n/a', '0', '(null)', '0/0'))
    return True


def definition(base, native):
    return fixed_dropin(base, native)
