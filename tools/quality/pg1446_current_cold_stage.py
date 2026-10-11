"""Immutable new-only guest tools stage, not a preparation/admission action."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=W/'pg1446-current-cold-stage-v1'
TOOLS=W/'pg1444-current-cold-tools-v2'
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(P/'known_hosts'),'-i',str(P/'vm-access'),'-p','22222','ubuntu@127.0.0.1']


def main():
    os.umask(0o077);OUT.mkdir(mode=0o700)
    fixed=json.loads((W/'pg1444-current-cold-frozen-v2.safe.json').read_bytes())
    assert fixed['actualExit']==0 and fixed['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
    for name,digest in fixed['fileHashes'].items():assert hashlib.sha256((TOOLS/name).read_bytes()).hexdigest()==digest
    archive=OUT/'tools.private.tar'
    subprocess.run(['tar','-cf',str(archive),'-C',str(TOOLS),'.'],check=True)
    archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    subprocess.run(SSH+['mkdir','-m','700','/home/ubuntu/pg1446-cold-stage-v1'],check=True)
    subprocess.run(['scp','-q','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(P/'known_hosts'),
                    '-i',str(P/'vm-access'),'-P','22222',str(archive),'ubuntu@127.0.0.1:/home/ubuntu/pg1446-cold-stage-v1/tools.private.tar'],check=True)
    code="""import json,os,hashlib,tarfile,pathlib
os.umask(0o077)
require=lambda x:None if x else (_ for _ in ()).throw(ValueError('fixed new cold stage refused'))
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
archive=pathlib.Path('/home/ubuntu/pg1446-cold-stage-v1/tools.private.tar')
require(hashlib.sha256(archive.read_bytes()).hexdigest()==ARCHIVE_SHA)
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1441-current-cold-tools-v1');require(not out.exists());out.mkdir(mode=0o700)
with tarfile.open(archive,'r:')as tar:
 for item in tar.getmembers():
  name=pathlib.PurePosixPath(item.name);require(not name.is_absolute() and '..'not in name.parts)
  require(item.isdir() and str(name)=='.'or item.isfile() and len(name.parts)==1)
 tar.extractall(out,filter='data')
for p in out.iterdir():
 require(p.is_file()and not p.is_symlink());os.chown(p,0,0);os.chmod(p,0o400)
 with p.open('rb')as f:os.fsync(f.fileno())
require({p.name for p in out.iterdir()}==set(HASHES)|{'payload-sha256.json'})
for name,digest in HASHES.items():require(hashlib.sha256((out/name).read_bytes()).hexdigest()==digest)
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({'run':'PG1446-current-cold-stage-v1','actualExit':0,'fileCount':len(list(out.iterdir())),'workerStartIssued':False,'permissionIssued':False,'formalAccepted':False}))
"""
    code='ARCHIVE_SHA='+repr(archive_sha)+'\nHASHES='+repr(fixed['fileHashes'])+'\n'+code
    with (OUT/'stage.private.log').open('xb')as log:
        result=subprocess.run(SSH+['sudo','-n','python3','-'],input=code.encode(),stdout=log,stderr=log)
    assert result.returncode==0
    safe=json.loads((OUT/'stage.private.log').read_bytes())
    safe.update(archiveSha256=archive_sha,frozenOperatorSource=fixed['operatorSource'])
    with (OUT/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe))


if __name__=='__main__':main()
