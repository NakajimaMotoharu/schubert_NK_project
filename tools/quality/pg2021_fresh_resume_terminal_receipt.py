"""Independent new-activation DONE/PID1 normal0or10 receipt; never start/stop authority."""
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2015_completed_run_fresh_resume_once import SOURCE

SLOT='pg2021-fresh-resume-terminal-receipt-v1'


def classify(binding,state,rows,done):
    import datetime
    def require(value):
        if not value:raise ValueError('current normal parent receipt refused')
    require(type(binding)is dict and type(state)is dict and type(rows)is list and type(done)is bytes)
    require(type(binding.get('start'))is int and binding['start']>0 and binding.get('activation')!='9adbf05a-61d0-408b-b51d-ab19c7e5b16a')
    fixed={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':'','Result':'success','ExecMainCode':'1','InvocationID':binding['invocation'],'SuccessExitStatus':'10','ExecMainStartTimestampMonotonic':str(binding['start'])}
    require(all(state.get(k)==v for k,v in fixed.items())and state.get('ExecMainStatus')in {'0','10'})
    end=state.get('ExecMainExitTimestampMonotonic');require(type(end)is str and end.isdecimal()and binding['start']<=int(end)<=binding['start']+1800000000)
    require(0<len(done)<=512 and done.endswith(b'\n'))
    fields=done.decode('ascii').splitlines();require(len(fields)==6 and fields[:4]==['NKDONE1',binding['run'],binding['cutoff'],binding['activation']]and fields[5]==state['ExecMainStatus'])
    ended=datetime.datetime.fromisoformat(fields[4].replace('Z','+00:00'));cutoff=datetime.datetime.fromisoformat(binding['cutoff'].replace('Z','+00:00'));require(ended.tzinfo is not None and cutoff<=ended)
    require(rows and all(type(r)is dict for r in rows))
    cursors=[r.get('__CURSOR')for r in rows];require(all(type(c)is str and c for c in cursors)and len(set(cursors))==len(cursors))
    common={'_BOOT_ID':binding['boot'],'_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':binding['invocation']}
    for r in rows:
        require(all(r.get(k)==v for k,v in common.items()))
        mono=r.get('__MONOTONIC_TIMESTAMP');require(type(mono)is str and mono.isdecimal()and binding['start']<=int(mono)<=binding['start']+1800000000)
    jobs=[r for r in rows if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_ID')==binding['job']and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='done']
    require(len(jobs)==1)
    forbidden={'be02cf6855d2428ba40df7e9d022f03d','98e322203f7a4ed290d09fe03c09fe15'}
    require(not any(r.get('MESSAGE_ID')in forbidden for r in rows))
    job=jobs[0];stamp=job.get('__REALTIME_TIMESTAMP');require(type(stamp)is str and stamp.isdecimal())
    real=datetime.datetime.fromtimestamp(int(stamp)/1000000,datetime.timezone.utc);require(ended<=real and (real-ended).total_seconds()<=60 and int(end)<=int(job['__MONOTONIC_TIMESTAMP'])<=int(end)+60000000)
    return {'genuineParentDone':True,'genuineRootDone':True,'genuinePid1StartDone':True,'newActivationSameRunCutoff':True,'completionCode':int(fields[5]),'completionOutcome':'WARNING'if fields[5]=='10'else'SUCCESS','normalUnit0or10':True,'endMonotonicUs':int(job['__MONOTONIC_TIMESTAMP']),'elapsedSeconds':(int(end)-binding['start'])/1000000,'wholeAccepted':False}


GUEST=r'''
import hashlib,json,os,pathlib,stat,subprocess
def require(v):
 if not v:raise ValueError('fresh readonly terminal identity refused')
def meta(s):return[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==BINDING['boot'])
release=pathlib.Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1846'and hashlib.sha256(manifest).hexdigest()=='ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7'and json.loads(manifest)['source']['commit']=='0fd734195b4d5338f6b7e860e087cce561d49562')
props=['ActiveState','SubState','MainPID','ControlPID','Job','Result','ExecMainCode','ExecMainStatus','InvocationID','SuccessExitStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic']
unit='schubert-nk-morning-controller.service'
def show():return dict(x.split('=',1)for x in subprocess.check_output(['systemctl','show',unit,'--property='+','.join(props)],text=True,timeout=5).splitlines())
def read(p):
 s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p));v=p.read_bytes();require(meta(p.lstat())==meta(s));return v
base=pathlib.Path('/var/lib/schubert-nk/maintenance');donepath=base/'attempts'/(BINDING['activation']+'.done');done=read(donepath)
require(read(base/'attempts'/(BINDING['activation']+'.begin'))==('NKACT1\n'+BINDING['run']+'\n'+BINDING['cutoff']+'\n'+BINDING['activation']+'\n').encode())
require(not os.path.lexists(base/'active')and not pathlib.Path('/proc/503613').exists())
state=show();cmd=['journalctl','--boot='+BINDING['boot'],'_PID=1','UNIT='+unit,'INVOCATION_ID='+BINDING['invocation'],'-o','json','--no-pager']
raw=subprocess.check_output(cmd,timeout=10);rows=[json.loads(line)for line in raw.splitlines()]
result=classify(BINDING,state,rows,done)
second=subprocess.check_output(cmd,timeout=10);again=[json.loads(line)for line in second.splitlines()];require(rows==again and show()==state and read(donepath)==done and not os.path.lexists(base/'active'))
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2021-fresh-resume-terminal-receipt-v1');os.umask(0o077);out.mkdir(mode=0o700);proofs={}
for name,value in [('done.private',done),('pid1-first.private.jsonl',raw),('pid1-second.private.jsonl',second),('parent-state.private.json',json.dumps(state,sort_keys=True).encode())]:
 with(out/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(value);f.flush();os.fsync(f.fileno())
 proofs[name]=hashlib.sha256(value).hexdigest()
for p in [out,out.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({**result,'actualExit':0,'proofHashes':proofs,'parentState':state,'activeAbsent':True,'startsStopsSqlWrites0':True,'rawExported':False}))
'''


def payload(binding):
    raw='BINDING='+repr(binding)+'\n'+inspect.getsource(classify)+'\n'+GUEST
    from pyflakes.api import check
    if check(raw,'<actual same new parent terminal readonly source>'):raise ValueError('all terminal globals required')
    compile(raw,'<same new activation normal parent terminal>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed terminal tools required')
    actual=json.loads((W/'pg2019-fresh-resume-live-binding-complete-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['productionSource']!=SOURCE:raise ValueError('actual current new activation binding required')
    terminal=[json.loads(l)for l in(W/'pg2010-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    if not any(r.get('terminalObserved')is True for r in terminal):raise ValueError('actual captured observer terminal required; do not replay')
    out=W/SLOT;out.mkdir(mode=0o700);raw=payload(actual['binding']);(out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=60)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
