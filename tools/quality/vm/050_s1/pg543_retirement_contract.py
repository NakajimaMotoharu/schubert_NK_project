"""SSC198/192/217 current-generation finite delta; no resource operations here."""
import re
import stat
from pg542_current_contract import UNITS, current_units, post_retirement_schema

MORNING = 'schubert-nk-morning-controller.service'
CADDY = 'caddy.service'
FIELDS = frozenset('Id LoadState ActiveState SubState MainPID ControlPID Job InvocationID ExecMainCode ExecMainStatus Result ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic KillMode SendSIGKILL Restart Type RemainAfterExit'.split())
CONFIG = frozenset('ExecStart DropInPaths ReadWritePaths User Group SupplementaryGroups NoNewPrivileges ProtectSystem ProtectHome PrivateTmp PrivateDevices RestrictSUIDSGID CapabilityBoundingSet AmbientCapabilities UMask LimitCORE TimeoutStartUSec TimeoutStopUSec MemoryMax TasksMax'.split())
NATIVE = '/etc/systemd/system/'+MORNING+'.d/pg477-native-coverage.conf'
RUNTIME = '/run/systemd/system/'+MORNING+'.d/pg492-once-resume.conf'
EMPTY = ('n/a', 'n/a', '0', '(null)', '0/0')


def release_metadata(value):
    require(isinstance(value,list) and len(value)==9 and all(type(v) is int for v in value))
    require(value[2:6]==[0,986,stat.S_IFREG|0o640,1] and 0<value[6]<=16384)
    return True


def require(value):
    if not value:
        raise ValueError('current runtime finite contract refused')


def record(value):
    if not isinstance(value, str) or len(value) > 65536:
        return None
    found = re.fullmatch(r'\{ path=([^ ;\r\n]+) ; argv\[\]=([^\r\n]*?) ; ignore_errors=(yes|no) ; start_time=\[([^\]\r\n]*)\] ; stop_time=\[([^\]\r\n]*)\] ; pid=([0-9]+) ; code=([^ ;\r\n]+) ; status=([^ ;\r\n]+) \}', value)
    if not found:
        return None
    v = found.groups()
    if not v[0].startswith('/') or any(t in v[1] for t in (' ; ignore_errors=', ' ; start_time=', ' ; stop_time=', ' ; pid=', ' ; code=', ' ; status=')):
        return None
    return v


def validate_snapshot(value):
    post_retirement_schema(value)
    current_units(value['units'])
    require(set(value['configuration']) == UNITS)
    for unit in UNITS:
        require(set(value['units'][unit]) == FIELDS and all(isinstance(v, str) for v in value['units'][unit].values()))
        c = value['configuration'][unit]
        require(isinstance(c, dict) and set(c) == CONFIG and all(isinstance(v, str) for v in c.values()) and record(c['ExecStart']) is not None)
    return True


def configurations(before, actual, expected_morning, before_caddy_pre, actual_caddy_pre):
    """Only Morning's independently authenticated no-resume declaration and paired Caddy reset."""
    require(set(before) == set(actual) == UNITS)
    for unit in UNITS:
        old, new = before[unit], actual[unit]
        require(set(old) == set(new) == CONFIG and all(isinstance(v, str) for v in [*old.values(), *new.values()]))
        allowed = {'ExecStart', 'DropInPaths'} if unit == MORNING else {'ExecStart'} if unit == CADDY else set()
        require(all(old[k] == new[k] for k in CONFIG - allowed))
        if not allowed:
            continue
        left, right = record(old['ExecStart']), record(new['ExecStart'])
        require(left is not None and right is not None)
        if unit == MORNING:
            require(type(expected_morning) is tuple and len(expected_morning) == 3)
            require(right[:3] == expected_morning and left[:3] != expected_morning)
            # Declaration changed: systemd either retains this exact saved supplement or clears it.
            require(right[3:] in (left[3:], EMPTY))
            require(old['DropInPaths'].split() == [NATIVE, RUNTIME] and new['DropInPaths'] == NATIVE)
        else:
            oldpre, newpre = record(before_caddy_pre), record(actual_caddy_pre)
            require(oldpre is not None and newpre is not None and right[:3] == left[:3] and oldpre[:3] == newpre[:3])
            require((right[3:], newpre[3:]) in ((left[3:], oldpre[3:]), (EMPTY, EMPTY)))
    return True


def phase_action(state, action, readonly=False):
    allowed = {'READY': {'before':'READY', 'removed':'VALIDATED'}, 'VALIDATED': {'release':'CLOSED'}}
    if readonly:
        allowed = {'READY': {'before':'READY', 'release':'CLOSED'}}
    require(action in allowed.get(state, {}))
    return allowed[state][action]
