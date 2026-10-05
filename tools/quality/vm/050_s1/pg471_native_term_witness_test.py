"""Literal manager/journal oracle: no production method computes expectations."""
import copy
import json
from pg471_native_term_witness import witness

checks = 0


def check(value):
    global checks
    checks += 1
    assert value


def rejected(role, before, after, rows, uid):
    try:
        witness(role, before, after, raw(rows), '42', uid)
    except ValueError:
        check(True)
        return
    raise AssertionError('invalid native TERM accepted')


def raw(rows):
    return ('\n'.join(json.dumps(r) for r in rows) + '\n').encode()


for role, uid in [('API', '999'), ('WEB', '997')]:
    before = dict(Id=f'schubert-nk-{role.lower()}.service', LoadState='loaded',
                  ActiveState='active', SubState='running', Job='', MainPID='42',
                  ControlPID='0', InvocationID='a' * 32, Type='simple', Restart='on-failure',
                  RemainAfterExit='no', Result='success', ExecMainCode='0', ExecMainStatus='0',
                  ExecMainStartTimestampMonotonic='100', ExecMainExitTimestampMonotonic='0',
                  KillMode='control-group', SendSIGKILL='no')
    after = {**before, 'ActiveState': 'failed', 'SubState': 'failed', 'MainPID': '0',
             'Result': 'exit-code', 'ExecMainCode': '1', 'ExecMainStatus': '143',
             'ExecMainExitTimestampMonotonic': '200'}
    rows = [{'__CURSOR': f'literal-{i}', '__MONOTONIC_TIMESTAMP': str(t),
             '_BOOT_ID': 'e07aa7061acd4e65b309d7f330f79d54',
             '_SYSTEMD_UNIT': before['Id'], '_SYSTEMD_INVOCATION_ID': 'a' * 32,
             '_PID': '42', '_UID': uid, 'PRIORITY': '6', 'MESSAGE': message}
            for i, (t, message) in enumerate([(100, 'ordinary init'),
                (140, f'{role} cleanup complete'), (150, f'{role} process stopped'),
                (160, f'{role} fixed PT native capture complete')])]
    result = witness(role, before, after, raw(rows), '42', uid)
    check(result['nativeCaptureComplete'] and not result['unitSuccess']
          and not result['oldToolCloseSuccess'] and not result['coverage100'])
    rejected(role, before, after, rows[:3], uid)
    v = copy.deepcopy(rows); v[3]['__CURSOR'] = 'literal-4'; v.append(v[3].copy())
    v[4]['__CURSOR'] = 'literal-5'; rejected(role, before, after, v, uid)
    rejected(role, before, after, [rows[0], rows[1], rows[3], rows[2]], uid)
    for key, value in [('_UID', '0'), ('__MONOTONIC_TIMESTAMP', '149'),
                       ('MESSAGE', f'{role} fixed PT native capture incomplete'),
                       ('_SYSTEMD_INVOCATION_ID', 'b' * 32), ('_PID', '43'),
                       ('PRIORITY', '3'), ('MESSAGE', 'java.lang.IllegalStateException')]:
        v = copy.deepcopy(rows); v[3][key] = value
        rejected(role, before, after, v, uid)
    a = {**after, 'ExecMainStatus': '0'}; rejected(role, before, a, rows, uid)
    a = {**after, 'MainPID': '42'}; rejected(role, before, a, rows, uid)
    v = copy.deepcopy(rows); del v[1]; rejected(role, before, after, v, uid)

print(f'PG471_NATIVE_TERM_ORACLE assertions={checks} mutation0=true productionPT0=true')
