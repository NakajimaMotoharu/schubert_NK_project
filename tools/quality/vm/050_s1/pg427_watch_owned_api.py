"""Finite isolated PG/PT actual peer observation + one owned Unit stop, never a ready oracle override."""
import datetime, hashlib, http.client, json, pathlib, re, subprocess, sys, time

assert sys.argv[1:] == []
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip() == 'pgpt-r2-20260927-01'
assert pathlib.Path('/opt/schubert-nk/current').readlink() == pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG425')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest() == '55353381ea39d2ddda0c3a195dea05cffda1ad880974693a72095811cd122fd1'
FIELDS = 'Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
MORNING, API = 'schubert-nk-morning-controller.service', 'schubert-nk-api.service'
INFO = {'commit': 'a3c86daf3ea1ac7ea9f6a3ae50dc45ead68c3fd2', 'app': '0.1.0-SNAPSHOT', 'config': '1', 'schema': '025', 'protocol': '0.1.0-SNAPSHOT'}

def show(unit):
    raw = subprocess.check_output(['/usr/bin/systemctl', 'show', unit, '--property=' + FIELDS], text=True, timeout=5)
    result = dict(line.split('=', 1) for line in raw.splitlines())
    assert len(result) == 18
    return result

def actor(unit):
    result = show(unit)
    pid = int(result['MainPID'])
    if pid:
        proc = pathlib.Path('/proc') / str(pid)
        try:
            result['startTicks'] = int((proc / 'stat').read_text().rpartition(')')[2].split()[19])
            result['process'] = {k: v.strip() for k, v in (line.split(':', 1) for line in (proc / 'status').read_text().splitlines() if ':' in line)
                                 if k in {'Uid', 'Gid', 'Groups', 'CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb', 'NoNewPrivs'}}
            cmd = (proc / 'cmdline').read_bytes().split(b'\0')
            result['entry'] = next((s.decode('ascii') for s in cmd if s in {
                b'dev.codex.schubert.nk.batch.file.RootServiceLauncher', b'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain'}), 'other')
        except (FileNotFoundError, ProcessLookupError):
            result['race'] = True
    return result

def same(before, after):
    return all(before.get(k) == after.get(k) for k in ('MainPID', 'InvocationID', 'startTicks', 'entry')) and not after.get('race')

def owns_socket(a):
    proc = pathlib.Path('/proc') / a['MainPID']
    targets = set()
    for descriptor in (proc / 'fd').iterdir():
        try:
            target = str(descriptor.readlink())
            if target.startswith('socket:['): targets.add(target[8:-1])
        except FileNotFoundError: pass
    ipv4 = (proc / 'net/tcp').read_text().splitlines()[1:]
    ipv6 = (proc / 'net/tcp6').read_text().splitlines()[1:]
    return listens(ipv4, targets, '0100007F:1F9B') or listens(
        ipv6, targets, '0000000000000000FFFF00000100007F:1F9B')

def listens(rows, targets, address):
    for row in rows:
        fields = row.split()
        if len(fields) >= 10 and fields[1] == address and fields[3] == '0A' and fields[9] in targets:
            return True
    return False

def get(path):
    connection = http.client.HTTPConnection('127.0.0.1', 8091, timeout=.5)
    try:
        connection.request('GET', path)
        response = connection.getresponse()
        body = response.read(4097)
        assert len(body) <= 4096
        return response.status, body
    finally: connection.close()

initial = actor(MORNING)
initial_api = actor(API)
assert initial['InvocationID'] == '6469d57202d9456ea8712e10102380b4' and initial['MainPID'] == '1396524' and initial['startTicks'] == 20656449
assert initial_api['InvocationID'] == 'c6015f169dc341169a24da58fdb01481' and initial_api['MainPID'] == '1494074' and initial_api['startTicks'] == 20721763 and initial_api['entry'] == 'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain'
# Observation only: never refresh or extend the Production 30-minute budget.
seen, stopped, ready, prior = False, False, False, None
deadline = time.monotonic() + 1900
if int(initial['MainPID']):
    deadline = min(deadline, int(initial['ExecMainStartTimestampMonotonic']) / 1_000_000 + 1860)
while time.monotonic() < deadline:
    m, a = actor(MORNING), actor(API)
    if int(m['MainPID']): assert same(initial, m)
    if int(a['MainPID']): assert same(initial_api, a)
    if int(m['MainPID']): seen = True
    key = json.dumps({'morning': m, 'api': a}, sort_keys=True)
    if key != prior:
        print(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'morning': m, 'api': a}), flush=True)
        prior = key
    if a.get('entry') == 'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain' and not a.get('race') and not stopped:
        p = a['process']
        assert p['Uid'].split() == ['999'] * 4 and p['Gid'].split() == ['981'] * 4 and p['NoNewPrivs'] == '1'
        assert all(p[k] == '0000000000000000' for k in ('CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb'))
        try:
            if owns_socket(a):
                status, body = get('/actuator/health/readiness')
                info_status, info = get('/actuator/info')
                if status == 200 and body == b'{"status":"UP"}' and info_status == 200 and json.loads(info) == INFO:
                    # Actual current actor owns the listening inode before and after HTTP; no Unit-active surrogate.
                    aa, mm = actor(API), actor(MORNING)
                    assert same(a, aa) and same(m, mm) and owns_socket(aa)
                    print(json.dumps({'actualApiReady': True, 'samePeerSocket': True, 'sameMorningGeneration': True,
                                      'mainPid': a['MainPID'], 'invocation': a['InvocationID'], 'startTicks': a['startTicks'], 'information': INFO}), flush=True)
                    ready = True
                    subprocess.run(['/usr/bin/systemctl', 'stop', API], check=True, timeout=70)
                    stopped = True
                    print(json.dumps({'ownedApiStopCompleted': True, 'readyBeforeStop': True}), flush=True)
        except (ConnectionError, OSError, http.client.HTTPException): pass
    if seen and all(v['MainPID'] == '0' and v['ControlPID'] == '0' and not v['Job'] for v in (m, a)):
        print(json.dumps({'terminalObserved': True, 'actualApiReady': ready, 'wholeMorningAccepted': False}), flush=True)
        break
    time.sleep(.1)
else:
    print(json.dumps({'watchDeadline': True, 'actualApiReady': ready, 'automaticUnknownStop': False, 'wholeMorningAccepted': False}), flush=True)
