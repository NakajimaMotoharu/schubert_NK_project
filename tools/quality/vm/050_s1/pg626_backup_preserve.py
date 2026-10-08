"""Read-only full prior Backup byte preservation before ordinary approved retention."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import hashlib,io,json,os,pathlib,stat,sys,tarfile
os.umask(0o077)
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg624-completed-activate-v1/after.private.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='11675ec02384a125f762014ebb1da251a2ab07c466aa8465bcd0f05ee284ce91'
baseline=json.loads(raw)['backup'];root=pathlib.Path('/srv/schubert-nk/backup')
assert {str(p)for p in [root,*root.rglob('*')]}==set(baseline)
def metadata(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
assert all(metadata(pathlib.Path(p))==v['metadata']for p,v in baseline.items())
catalog={};count=0
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|')as tar:
 for name,v in sorted(baseline.items()):
  p=pathlib.Path(name)
  if v['sha256']is None and p!=root:
   info=tarfile.TarInfo(p.relative_to(root).as_posix());info.type=tarfile.DIRTYPE;info.mode=0o700;info.uid=v['metadata'][2];info.gid=v['metadata'][3];tar.addfile(info)
 for name,v in sorted(baseline.items()):
  if v['sha256']is None:continue
  p=pathlib.Path(name);assert not p.is_symlink()and stat.S_ISREG(p.lstat().st_mode)and p.lstat().st_nlink==1
  fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb')as f:content=f.read()
  assert metadata(p)==v['metadata']and hashlib.sha256(content).hexdigest()==v['sha256']
  relative=p.relative_to(root).as_posix();info=tarfile.TarInfo(relative);info.size=len(content);info.mode=0o600;tar.addfile(info,io.BytesIO(content));catalog[relative]={'sha256':v['sha256'],'bytes':len(content)};count+=1
 assert count==sum(v['sha256']is not None for v in baseline.values())and count>28
 assert all(metadata(pathlib.Path(p))==v['metadata']for p,v in baseline.items())
 safe=json.dumps({'files':catalog,'fileCount':count,'eligibleBundles':7,'protectedNames':5,'treeMetadata':baseline,'backupUnchanged':True,'currentSource':'72fb7440697ee1048a5c0145055dc1cc3c577914'}).encode()
 info=tarfile.TarInfo('catalog.safe.json');info.size=len(safe);info.mode=0o600;tar.addfile(info,io.BytesIO(safe))
'''


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    bundle=P/'pg626-prior-seven-backups.private.tar'
    log=W/'pg626-backup-preserve-v1.private.log'
    assert not bundle.exists()and not log.exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    with bundle.open('xb')as out,log.open('xb')as err:
        result=subprocess.run(ssh,input=PAYLOAD.encode(),stdout=out,stderr=err,timeout=90)
        for f in (out,err):f.flush();os.fsync(f.fileno())
    assert result.returncode==0
    with tarfile.open(bundle)as tar:
        members=tar.getmembers();regular=[m for m in members if m.isfile()];directories=[m for m in members if m.isdir()]
        assert len(directories)==12 and len(regular)==35 and len(members)==47
        assert all(not m.issym()and not m.islnk()and m.mode==0o600 for m in regular)
        assert all(m.mode==0o700 and m.uid==992 and m.gid==977 for m in directories)
        catalog=json.loads(tar.extractfile('catalog.safe.json').read())
        assert len(regular)==catalog['fileCount']+1
        assert {m.name for m in regular}==set(catalog['files'])|{'catalog.safe.json'}
        expected_dirs={Path(n).relative_to('/srv/schubert-nk/backup').as_posix()for n,v in catalog['treeMetadata'].items()if v['sha256']is None and n!='/srv/schubert-nk/backup'}
        assert {m.name.rstrip('/')for m in directories}==expected_dirs
        for name,v in catalog['files'].items():
            content=tar.extractfile(name).read();assert len(content)==v['bytes']and hashlib.sha256(content).hexdigest()==v['sha256']
    safe={'actualExit':0,'priorFiles':catalog['fileCount'],'priorEligibleBundles':7,'priorProtectedNames':5,'privateArchiveSha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'privateArchiveBytes':bundle.stat().st_size,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'rawExported':False,'serverMutations':0,'formalAccepted':False}
    with(W/'pg626-backup-preserve-v1.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(safe))


if __name__=='__main__':main()
