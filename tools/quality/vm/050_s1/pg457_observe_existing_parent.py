"""Attach to the actual PG456 retained parent; observe original deadline, never start/stop."""
import datetime
import json
import pathlib
import subprocess
import time

assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip() == 'e07aa706-1acd-4e65-b309-d7f330f79d54'
UNITS = ['schubert-nk-morning-controller.service', 'schubert-nk-api.service', 'schubert-nk-web.service', 'caddy.service', 'artemis.service']
FIELDS = 'Id,LoadState,ActiveState,SubState,Job,InvocationID,Type,Restart,RemainAfterExit,MainPID,ControlPID,Result,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,ExecMainCode,ExecMainStatus,KillMode,SendSIGKILL'
def observed(unit):
    raw = subprocess.check_output(['/usr/bin/systemctl', 'show', unit, '--property=' + FIELDS], text=True, timeout=5)
    result = dict(line.split('=', 1) for line in raw.splitlines())
    assert len(result) == 18
    return result
initial = observed(UNITS[0])
assert initial['MainPID'] == '19114' and initial['InvocationID'] == '0735b37478204b49a5b2810c882ee3be'
deadline = int(initial['ExecMainStartTimestampMonotonic']) / 1e6 + 1860
previous = None
while time.monotonic() < deadline:
    states = [observed(unit) for unit in UNITS]
    parent = states[0]
    assert parent['InvocationID'] == initial['InvocationID']
    if parent['MainPID'] != '0':
        assert parent['MainPID'] == initial['MainPID']
    snapshot = json.dumps(states, sort_keys=True)
    if snapshot != previous:
        print(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'states': states,
                          'wholeMorningAccepted': False, 'automaticStop': False}), flush=True)
        previous = snapshot
    if parent['MainPID'] == '0' and parent['ControlPID'] == '0' and parent['Job'] == '':
        print(json.dumps({'terminalObserved': True, 'parentResult': parent['Result'],
                          'parentCode': parent['ExecMainCode'], 'parentExit': parent['ExecMainStatus'],
                          'wholeMorningAccepted': False, 'automaticStop': False}), flush=True)
        break
    time.sleep(2)
else:
    print(json.dumps({'observationDeadline': True, 'wholeMorningAccepted': False, 'automaticStop': False}), flush=True)
