"""One fixed old-holder data-only diagnostic; no Session, DB mutation, Unit or signal."""
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')

GUEST=r'''
import pathlib,os,hashlib,base64,json,subprocess,stat
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cbca8738-3b24-4090-b77c-bf029677cdd6'
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
p=pathlib.Path('/proc/5463');assert int((p/'stat').read_text().rpartition(')')[2].split()[19])==1373880
assert hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='fcb09442d0ad0bc9d0b71433c7a01f54b1c86941f3ab42e0c1cd6ba4f9f311c8'
assert str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'
status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
assert status['Uid'].split()==status['Gid'].split()==['0']*4
assert {int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}=={5489}
assert not pathlib.Path('/run/schubert-nk/startup').exists()and not pathlib.Path('/run/schubert-nk/pt-coverage').exists()
parent=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-prepared-v1');s=parent.lstat();assert stat.S_ISDIR(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o700
root=parent/'diagnostic-v1';assert not os.path.lexists(root);root.mkdir(mode=0o700)
classdir=root/'dev/codex/schubert/nk/batch/file';classdir.mkdir(parents=True,mode=0o700)
for ancestor in (root/'dev',root/'dev/codex',root/'dev/codex/schubert',root/'dev/codex/schubert/nk',root/'dev/codex/schubert/nk/batch',classdir):ancestor.chmod(0o700)
target=classdir/'Pg1040ColdRunPolicyProbe.class';data=base64.b64decode(CLASS_BASE64,validate=True);assert hashlib.sha256(data).hexdigest()==CLASS_SHA
with target.open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(data);f.flush();os.fsync(f.fileno())
cp=str(root)+':/opt/schubert-nk/releases/0.1.0-PG932/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG932/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG932/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG932/api/lib/*'
result=subprocess.run(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'dev.codex.schubert.nk.batch.file.Pg1040ColdRunPolicyProbe'],capture_output=True,timeout=60)
assert len(result.stdout)+len(result.stderr)<=65536
with(root/'diagnostic.private.log').open('xb')as f:f.write(result.stdout);f.write(result.stderr);f.flush();os.fsync(f.fileno())
print(result.stdout.decode('ascii'),end='');print(result.stderr.decode('ascii'),end='')
print(json.dumps({'actualExit':result.returncode,'dataOnly':True,'runAuthority':False,'oldOwnerUntouched':True,'diagnosticLogSha256':hashlib.sha256(result.stdout+result.stderr).hexdigest()}))
raise SystemExit(result.returncode)
'''


def main():
    os.umask(0o077)
    out=W/'pg1041-cold-policy-diagnostic-v1';out.mkdir(mode=0o700)
    root=W/'pg1040-cold-policy-probe-v2';compiled=json.loads((root/'compile.safe.json').read_bytes())
    if compiled['actualExit']!=0:raise ValueError('compiled readonly probe required')
    name='dev/codex/schubert/nk/batch/file/Pg1040ColdRunPolicyProbe.class';data=(root/name).read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    if digest!=compiled['classHashes'][name]:raise ValueError('probe class changed')
    raw='CLASS_BASE64='+repr(base64.b64encode(data).decode())+'\nCLASS_SHA='+repr(digest)+'\n'+GUEST
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=raw.encode(),capture_output=True,timeout=90)
    with(out/'diagnostic.private.log').open('xb')as f:f.write(result.stdout);f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe={'run':'PG1041-cold-policy-diagnostic-v1','actualExit':result.returncode,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classSha256':digest,'scriptSha256':hashlib.sha256(raw.encode()).hexdigest(),'logSha256':hashlib.sha256(result.stdout+result.stderr).hexdigest(),'dataOnly':True,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    # Only fixed probe vocabulary (native metadata/type, no record contents).
    for line in (result.stdout+result.stderr).decode('ascii').splitlines():
        if line.startswith('PG1040_'):print(line)
    print(json.dumps(safe));raise SystemExit(result.returncode)


if __name__=='__main__':main()
