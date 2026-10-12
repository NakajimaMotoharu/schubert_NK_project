"""Preserve actual Root13 WARNING/systemd failure, not acceptance or stop authority.

NK-OPS-001; SS341/343/353; BUG1162/YKT930; PT-OPS-WARN1764.
Only fixed readonly observations; secret-bearing original/journal stay guest root0600.
"""
import hashlib
import json
import os
import subprocess

from pg1446_current_cold_stage import P, SSH, W
from pg1674_critical_management_gate import management_gate
from pg1762_next_day_done_receipt import EXPECTED

SLOT = 'pg1764-warning-terminal-capture-v1'


def classify(state, fields):
    import datetime
    if type(state) is not dict or type(fields) is not list:
        raise ValueError('complete observation required')
    required = {'ActiveState':'failed', 'SubState':'failed', 'MainPID':'0',
                'Result':'exit-code', 'ExecMainCode':'1', 'ExecMainStatus':'10',
                'InvocationID':EXPECTED['invocation'], 'SuccessExitStatus':''}
    if any(state.get(k) != v for k, v in required.items()):
        raise ValueError('actual retained warning failure required')
    if len(fields) != 6 or fields[:4] != ['NKDONE1',EXPECTED['run'],EXPECTED['cutoff'],EXPECTED['activation']] or fields[5] != '10':
        raise ValueError('actual warning original required')
    ended=datetime.datetime.fromisoformat(fields[4].replace('Z','+00:00'))
    cutoff=datetime.datetime.fromisoformat(EXPECTED['cutoff'].replace('Z','+00:00'))
    if ended.tzinfo is None or not cutoff <= ended <= cutoff+datetime.timedelta(minutes=30):
        raise ValueError('actual DONE time required')
    start = state.get('ExecMainStartTimestampMonotonic')
    end = state.get('ExecMainExitTimestampMonotonic')
    if start != str(EXPECTED['start']) or type(end) is not str or not end.isdecimal() or not EXPECTED['start'] <= int(end) <= EXPECTED['start']+1800000000:
        raise ValueError('actual original parent budget required')
    return {'warningOriginalObserved':True, 'managerCompletion':'FAILED_EXIT10',
            'elapsedSeconds':(int(end)-EXPECTED['start'])/1000000,
            'wholeAccepted':False, 'startsStopsSqlWrites':0}


def payload():
    import inspect
    raw = 'EXPECTED='+repr(EXPECTED)+'\n'+inspect.getsource(classify)
    raw += r'''
import hashlib,json,os,pathlib,stat,subprocess
require=lambda x:None if x else (_ for _ in ()).throw(ValueError('warning evidence refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==EXPECTED['boot'])
base=pathlib.Path('/var/lib/schubert-nk/maintenance')
names=['schubert-nk-morning-controller.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service','schubert-nk-bootstrap-admin.service']
props=['ActiveState','SubState','MainPID','Result','ExecMainCode','ExecMainStatus','InvocationID','SuccessExitStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic','Job','ControlPID']
def show(n):
 return dict(x.split('=',1)for x in subprocess.check_output(['systemctl','show',n]+['-p'+p for p in props],text=True,timeout=5).splitlines())
def read(p):
 a=p.lstat();require(stat.S_ISREG(a.st_mode)and a.st_uid==a.st_gid==0 and stat.S_IMODE(a.st_mode)==0o600 and a.st_nlink==1)
 data=p.read_bytes();b=p.lstat();require(tuple(getattr(a,k)for k in ['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'])==tuple(getattr(b,k)for k in ['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']))
 return data
units={n:show(n)for n in names}
donepath=base/'attempts'/(EXPECTED['activation']+'.done');done=read(donepath)
result=classify(units[names[0]],done.decode('ascii').splitlines())
require(not os.path.lexists(base/'active'))
cmd=['journalctl','--boot='+EXPECTED['boot'],'_PID=1','UNIT='+names[0],'INVOCATION_ID='+EXPECTED['invocation'],'-o','json','--no-pager']
journal=subprocess.check_output(cmd,timeout=10)
rows=[json.loads(line)for line in journal.splitlines()]
require(rows and all(r.get('_PID')=='1'and r.get('_UID')=='0'and r.get('INVOCATION_ID')==EXPECTED['invocation']and r.get('_BOOT_ID')==EXPECTED['boot']for r in rows))
require({n:show(n)for n in names}==units and read(donepath)==done and subprocess.check_output(cmd,timeout=10)==journal)
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1764-warning-terminal-capture-v1');os.umask(0o077);out.mkdir(mode=0o700)
proofs={}
for name,data in [('done.private',done),('pid1.private.jsonl',journal),('units.private.json',json.dumps(units,sort_keys=True).encode())]:
 with(out/name).open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
 proofs[name]=hashlib.sha256(data).hexdigest()
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({**result,'proofHashes':proofs,'retainedRoot':units[names[0]],'unitCount':len(units),'activeAbsent':True,'rawPrinted':False}))
'''
    compile(raw,'<fixed warning observation>','exec')
    return raw


def main():
    os.umask(0o077)
    raw=payload().encode()
    out=W/SLOT
    out.mkdir(mode=0o700)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    safe={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'wholeAccepted':False}
    if r.returncode==0:safe['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe))
    return r.returncode


if __name__=='__main__':raise SystemExit(main())
