"""BUG792/YKT564: fixed catalog + loaded identity. Observation, never start/close authority."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

UNITS = ['caddy.service', 'schubert-nk-web.service', 'schubert-nk-api.service',
         'schubert-nk-cleanup.service', 'schubert-nk-inbox-inspector.service',
         'schubert-nk-expiry-cleanup.service', 'schubert-nk-backup.service',
         'artemis.service', 'schubert-nk-morning-controller.service',
         'schubert-nk-bootstrap-admin.service']
PROPERTIES = ['Id', 'LoadState', 'ActiveState', 'SubState', 'Job', 'MainPID', 'ControlPID',
              'InvocationID', 'ExecMainCode', 'ExecMainStatus', 'ExecMainStartTimestampMonotonic',
              'ExecMainExitTimestampMonotonic', 'Result', 'Type', 'Restart', 'RemainAfterExit',
              'KillMode', 'SendSIGKILL']
def parse(unit, text):
    if unit not in UNITS:
        raise ValueError('unknown fixed Unit')
    values = {}
    for line in text.splitlines():
        key, value = line.split('=', 1)
        if key not in PROPERTIES or key in values:
            raise ValueError('property set invalid')
        values[key] = value
    if set(values) != set(PROPERTIES) or values['Id'] != unit or values['LoadState'] != 'loaded':
        raise ValueError('actual loaded identity unavailable')
    return values

if '--self-test' in sys.argv:
    count = 0
    for unit in UNITS:
        literal = '\n'.join(p+'='+({'Id': unit, 'LoadState': 'loaded'}.get(p, '0')) for p in PROPERTIES)+'\n'
        assert parse(unit, literal)['Id'] == unit
        count += 1
        for bad in [literal.replace('LoadState=loaded', 'LoadState=not-found'),
                    literal.replace('Id='+unit, 'Id=schubert-nk-morning.service'),
                    literal.replace('LoadState=loaded\n', ''), literal+'Id='+unit+'\n']:
            try:
                parse(unit, bad)
                raise AssertionError('invalid loaded identity accepted')
            except ValueError:
                count += 1
    try:
        parse('schubert-nk-morning.service', '')
        raise AssertionError('unknown alias accepted')
    except ValueError:
        count += 1
    print(json.dumps({'independentAssertions': count, 'actualExit': 0, 'vmActions': 0}))
    sys.exit(0)

os.umask(0o077)
private = Path('/home/mini/codex/project1/work/pgpt-vm/private')
out = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg488-current-units-readonly-v1.private.json')
assert not out.exists()
ssh = ['ssh', '-i', str(private/'vm-access'), '-p', '22222', '-oBatchMode=yes',
       '-oIdentitiesOnly=yes', '-oStrictHostKeyChecking=yes',
       '-oUserKnownHostsFile='+str(private/'known_hosts'), 'ubuntu@127.0.0.1']
boot = subprocess.check_output(ssh+['cat /proc/sys/kernel/random/boot_id'], text=True).strip()
def read():
    return {unit: parse(unit, subprocess.check_output(ssh+[
        'systemctl show '+unit+' --property='+','.join(PROPERTIES)], text=True)) for unit in UNITS}
before = read()
after = read()
assert before == after
assert subprocess.check_output(ssh+['cat /proc/sys/kernel/random/boot_id'], text=True).strip() == boot
jobs = subprocess.check_output(ssh+['systemctl list-jobs --no-legend'], text=True)
assert not jobs.strip()
value = {'captured': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'boot': boot,
         'units': after, 'jobs': 0, 'readonly': True, 'oldCloseNotInferred': True}
with out.open('x') as stream:
    json.dump(value, stream, sort_keys=True)
parent = after['schubert-nk-morning-controller.service']
print(json.dumps({'actualExit': 0, 'boot': boot, 'units': len(after), 'allLoaded': True,
                  'parent': parent, 'jobs': 0, 'starts': 0, 'oldCloseNotInferred': True}))
