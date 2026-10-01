"""Independent, read-only Work/private generation observations; no readiness oracle."""
import datetime, json, pathlib, subprocess, time
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip() == 'pgpt-r2-20260927-01'
units = ['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service']
fields = 'Id,ActiveState,SubState,MainPID,ControlPID,InvocationID,Job,ExecMainStatus,ExecMainStartTimestampMonotonic'
seen, previous = False, None
deadline = time.monotonic() + 1900
while time.monotonic() < deadline:
    rows = {}
    for unit in units:
        raw = subprocess.check_output(['/usr/bin/systemctl','show',unit,'--property='+fields], text=True)
        row = dict(line.split('=',1) for line in raw.splitlines())
        pid = int(row['MainPID'])
        if pid:
            if unit == units[0]: seen = True
            proc = pathlib.Path('/proc')/str(pid)
            try:
                row['exe'] = str((proc/'exe').readlink())
                status = (proc/'status').read_text()
                row['process'] = {line.split(':',1)[0]:line.split(':',1)[1].strip()
                                  for line in status.splitlines()
                                  if line.split(':',1)[0] in {'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}}
                row['cgroup'] = (proc/'cgroup').read_text().strip()
                cmd = (proc/'cmdline').read_bytes().split(b'\0')
                row['entry'] = next((s.decode('ascii') for s in cmd if s in [
                    b'dev.codex.schubert.nk.batch.file.RootServiceLauncher',
                    b'dev.codex.schubert.nk.api.bootstrap.ApiProcessMain',
                    b'dev.codex.schubert.nk.web.bootstrap.WebProcessMain']), 'other')
                row['fdCount'] = len(list((proc/'fd').iterdir()))
            except (FileNotFoundError, ProcessLookupError):
                row['observationRace'] = True
        rows[unit] = row
    encoded = json.dumps(rows, sort_keys=True)
    if encoded != previous:
        print(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'units':rows}), flush=True)
        previous = encoded
    if seen and all(r['MainPID']=='0' and r['ControlPID']=='0' and not r['Job'] for r in rows.values()):
        print(json.dumps({'terminalObserved':True,'readyClaimed':False}), flush=True)
        break
    time.sleep(.1)
else:
    print(json.dumps({'watchDeadline':True,'readyClaimed':False}), flush=True)
