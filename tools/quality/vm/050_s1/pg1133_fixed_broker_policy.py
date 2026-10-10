"""SSC256: independently bounded sole-broker terminal/configuration projection."""
import re

PID = '253968'
INV = '0f751fba26c94b22ac693a839fced07d'
MUTABLE = {'ActiveState', 'SubState', 'MainPID', 'ControlPID', 'Job', 'Result',
           'ExecMainCode', 'ExecMainStatus', 'ExecMainExitTimestampMonotonic'}


def require(value):
    if not value: raise ValueError('fixed current broker transition refused')


def stopped(before, after):
    require(type(before) is dict and type(after) is dict and set(before) == set(after))
    require(before['MainPID'] == PID and before['InvocationID'] == INV and
            before['ActiveState'] == 'active' and before['SubState'] == 'running')
    require(all(before[key] == after[key] for key in before.keys() - MUTABLE))
    require(after['MainPID'] == after['ControlPID'] == '0' and after['Job'] == '' and
            after['ActiveState'] == 'inactive' and after['SubState'] == 'dead' and
            after['Result'] == 'success' and after['ExecMainCode'] == '1' and after['ExecMainStatus'] == '143')
    require(type(after['ExecMainExitTimestampMonotonic']) is str and after['ExecMainExitTimestampMonotonic'].isdigit()
            and int(after['ExecMainExitTimestampMonotonic']) >= int(before['ExecMainStartTimestampMonotonic']))
    return True


def configuration(before, after, unit_before, unit_after, parse):
    require(type(before) is dict and type(after) is dict and set(before) == set(after))
    if unit_before == unit_after:
        require(before == after); return True
    stopped(unit_before, unit_after)
    require(all(before[key] == after[key] for key in before.keys() - {'ExecStart'}))
    old = parse(before['ExecStart']); new = parse(after['ExecStart'])
    require(old is not None and new is not None and old[:3] == new[:3])
    # Full parsed primary history is retained below: same start/PID; only end/code/status changes.
    require(old[3] == new[3] and old[5] == new[5] and new[6:] == ('exited', '143'))
    require(new[4] != old[4] and unit_after['ExecMainExitTimestampMonotonic'] != '0')
    return True
