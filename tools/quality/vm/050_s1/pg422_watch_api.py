"""Finite isolated PG/PT actual peer observation + one owned Unit stop, never a ready oracle override."""
import datetime, hashlib, http.client, json, pathlib, subprocess, time

assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip() == 'pgpt-r2-20260927-01'
assert pathlib.Path('/opt/schubert-nk/current').readlink() == pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG421')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest() == '2348f978fafc1cdd521e1d866ca8fa3ae13d220668b266e0d989d0087cfa7979'
FIELDS = 'Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
MORNING, API = 'schubert-nk-morning-controller.service', 'schubert-nk-api.service'
INFO = {'commit': '995d3c5386f09b89bc4af4a2e7c9d3fdb9f603e3', 'app': '0.1.0-SNAPSHOT', 'config': '001', 'schema': '025', 'protocol': '001'}

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
    return any(len(row.split()) >= 10 and row.split()[1] == '0100007F:1F9B' and row.split()[3] == '0A'
               and row.split()[9] in targets for row in (proc / 'net/tcp').read_text().splitlines()[1:])

def get(path):
    connection = http.client.HTTPConnection('127.0.0.1', 8091, timeout=.5)
    try:
        connection.request('GET', path)
        response = connection.getresponse()
        body = response.read(4097)
        assert len(body) <= 4096
        return response.status, body
    finally: connection.close()

seen, stopped, ready, prior = False, False, False, None
deadline = time.monotonic() + 240
while time.monotonic() < deadline:
    m, a = actor(MORNING), actor(API)
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
