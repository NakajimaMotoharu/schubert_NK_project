"""SS343/SSC188189196 current existing-ADMIN fixture pure invariants, no runtime authority."""
import re
import ctypes

UNIT = 'schubert-nk-bootstrap-admin.service'
FIELDS = frozenset('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))
SOURCES = frozenset(('bootstrap-admin-username', 'bootstrap-admin-password'))


def require(value):
    if not value:
        raise ValueError('fixed existing bootstrap scope unavailable')


def entry(value):
    require(isinstance(value, dict) and set(value) == {'metadata', 'sha256'})
    meta = value['metadata']
    require(isinstance(meta, list) and len(meta) == 9 and all(type(n) is int for n in meta)
            and meta[0] != 0 and meta[1] != 0 and meta[6] >= 0)
    sha = value['sha256']
    require(sha is None or isinstance(sha, str) and re.fullmatch('[0-9a-f]{64}', sha))
    return meta


def retire_no_replace(source_fd, name, target_fd, call=None):
    require(type(source_fd) is int and source_fd >= 0
            and type(target_fd) is int and target_fd >= 0 and name in SOURCES)
    if call is None:
        library = ctypes.CDLL(None, use_errno=True)
        call = library.renameat2
        call.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        call.restype = ctypes.c_int
    # Same Linux RENAME_NOREPLACE=1 contract as the admitted DirectoryCalls SPI.
    require(call(source_fd, name.encode('ascii'), target_fd,
                 (name + '.retired.private').encode('ascii'), 1) == 0)


def normal20(value):
    return (isinstance(value, dict) and set(value) == FIELDS
            and all(isinstance(x, str) for x in value.values())
            and value['Id'] == UNIT and value['LoadState'] == 'loaded'
            and value['Type'] == 'oneshot' and value['Restart'] == 'no'
            and value['RemainAfterExit'] == 'no' and value['KillMode'] == 'control-group'
            and value['SendSIGKILL'] == 'no'
            and value['MainPID'] == value['ControlPID'] == '0' and value['Job'] == ''
            and value['ActiveState'] == 'inactive' and value['SubState'] == 'dead'
            and value['Result'] == 'success' and value['ExecMainCode'] == '1'
            and value['ExecMainStatus'] == '20'
            and re.fullmatch(r'(?!0{32}$)[0-9a-f]{32}', value['InvocationID']) is not None
            and re.fullmatch('[1-9][0-9]{0,18}', value['ExecMainStartTimestampMonotonic']) is not None
            and re.fullmatch('[1-9][0-9]{0,18}', value['ExecMainExitTimestampMonotonic']) is not None
            and int(value['ExecMainExitTimestampMonotonic']) <= 9223372036854775807
            and 0 < int(value['ExecMainStartTimestampMonotonic'])
            <= int(value['ExecMainExitTimestampMonotonic'])
            <= int(value['ExecMainStartTimestampMonotonic']) + 30000000)


def same_terminal_cohort(before, actual, terminal=None):
    require(isinstance(before, dict) and isinstance(actual, dict) and set(before) == set(actual)
            and UNIT in before)
    for unit, previous in before.items():
        if unit == UNIT and terminal is not None:
            require(normal20(terminal) and actual[unit] == terminal)
            require(previous['InvocationID'] != terminal['InvocationID'])
        else:
            require(actual[unit] == previous)


def credential_tree(before, actual, prepared):
    """Only new sources and their directory timestamps change; all other original bytes retained."""
    require(isinstance(before, dict) and isinstance(actual, dict) and isinstance(prepared, dict))
    root = '/etc/schubert-nk/credentials'
    expected = {root + '/' + name for name in SOURCES}
    require(root in before and root in actual and expected.isdisjoint(before))
    require(set(actual) == set(before) | set(prepared) and set(prepared) <= expected)
    for path, old in before.items():
        new = actual[path]
        entry(old)
        entry(new)
        if path == root:
            require(new['metadata'][:6] == old['metadata'][:6]
                    and new['sha256'] == old['sha256'] is None)
        else:
            require(new == old)
    for path, expected_value in prepared.items():
        require(actual[path] == expected_value)
        meta = entry(expected_value)
        require(meta[2:6] == [0, 0, 0o100400, 1] and 0 < meta[6] <= 256)


def completion_messages(messages):
    require(type(messages)is list and all(type(v)is str for v in messages))
    ordered=('Initial ADMIN bootstrap finished','Bootstrap fixed PT native capture complete',
             'Bootstrap fixed PT native closing complete')
    require(all(messages.count(v)==1 for v in ordered) and 'Initial ADMIN bootstrap failed'not in messages)
    require(messages.index(ordered[0])<messages.index(ordered[1])<messages.index(ordered[2]))


def native_tree(before, actual, invocation=None):
    """SSC234 two physical exports, exactly one ordinary Bootstrap JVM session."""
    require(isinstance(before, dict) and isinstance(actual, dict))
    role='/run/schubert-nk/pt-coverage/ordinary-bootstrap196'
    require(role in before and role in actual)
    for value in [*before.values(),*actual.values()]:entry(value)
    if invocation is None:
        require(actual==before);return
    require(isinstance(invocation,str) and re.fullmatch(r'(?!0{32}$)[0-9a-f]{32}',invocation))
    fresh={role+'/'+invocation+'.'+point+'.exec'for point in ('terminal','closing')}
    require(fresh.isdisjoint(before) and set(actual)==set(before)|fresh)
    for name,old in before.items():
        new=actual[name]
        if name==role:require(new['metadata'][:6]==old['metadata'][:6] and new['sha256']==old['sha256']is None)
        else:require(new==old)
    identities=set()
    for path in sorted(fresh):
        value=actual[path];meta=entry(value)
        require(meta[2:6]==[999,981,0o100600,1] and 5<=meta[6]<=16777216
            and isinstance(value['sha256'],str) and re.fullmatch('[0-9a-f]{64}',value['sha256']))
        require(tuple(meta[:2])not in identities);identities.add(tuple(meta[:2]))
