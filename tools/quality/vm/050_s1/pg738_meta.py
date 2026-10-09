"""Readonly hashes/actor timing from actual completed737; no secret input/DB output."""
import datetime
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import hashlib,json,os,pathlib,stat
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg737-bootstrap-existing-v1')
def strict(name,limit):
 p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not os.listxattr(p)and 0<s.st_size<=limit
 v=p.read_bytes();a=p.lstat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);return v
before=strict('before.private.json',67108864);after=strict('after.private.json',67108864)
actor=json.loads(strict('actor.private.json',4096));a=json.loads(after);u=a['units']['schubert-nk-bootstrap-admin.service']
assert strict('complete.private',4096)==b'allNewScopesReturnedNormally=true\nall24DatabaseUnchanged=true\nmode=execute\n'
assert u['ExecMainStatus']=='20'and not pathlib.Path('/proc',actor['pid']).exists()
start=int(u['ExecMainStartTimestampMonotonic']);end=int(u['ExecMainExitTimestampMonotonic']);assert 0<end-start<30000000
print(json.dumps({'actualExit':0,'beforeSha256':hashlib.sha256(before).hexdigest(),'afterSha256':hashlib.sha256(after).hexdigest(),
 'pid':actor['pid'],'ticks':actor['ticks'],'invocation':actor['invocation'],'startMonotonicUs':start,'endMonotonicUs':end,'elapsedSeconds':(end-start)/1000000,
 'batchRows':len(a['rows']['schubert.batch_runs']),'unitExit20':True,'allNewScopesReturnedNormally':True,'rawExported':False}))
'''


def main():
    os.umask(0o077)
    assert (W/'pg737-bootstrap-execute-v1.safe.json').is_file()
    safe=json.loads((W/'pg737-bootstrap-execute-v1.safe.json').read_bytes());assert type(safe['actualExit'])is int and safe['actualExit']==0
    out=W/'pg738-actual-admin-meta-v1.safe.json';err=W/'pg738-actual-admin-meta-v1.private.stderr';assert not out.exists()and not err.exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    with err.open('xb')as f:
        r=subprocess.run(ssh,input=PAYLOAD.encode(),stdout=subprocess.PIPE,stderr=f,timeout=30);f.flush();os.fsync(f.fileno())
    assert r.returncode==0
    v=json.loads(r.stdout);assert v['batchRows']==534
    v.update(recordedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip())
    with out.open('x')as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(v))


if __name__=='__main__':main()
