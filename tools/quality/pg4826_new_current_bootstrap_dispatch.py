"""SSC300 new-only stage/verify/one existing20 start; no Root or lifecycle replay."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from pg1446_current_cold_stage import SSH,P
from pg1674_critical_management_gate import management_gate
from pg4434_current_candidate_admission_read import authenticate_host
import pg4820_new_current_bootstrap_sources as role

W=role.W
SLOT='pg4826-new-current-bootstrap'
REMOTE='/home/ubuntu/pg4826-new-current-bootstrap-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS

STAGE=r'''
import hashlib,json,os,pathlib,stat,tarfile
def require(v):
 if not v:raise ValueError('current Bootstrap closed nested stage refused')
def inventory(files):
 require(type(files)is dict and bool(files))
 for name,digest in files.items():
  require(type(name)is str and name and not name.startswith('/')and '\\'not in name and all(p not in ('','.','..')for p in name.split('/')))
  require(type(digest)is str and len(digest)==64 and all(c in '0123456789abcdef'for c in digest))
 names=set(files)|{'payload-sha256.json'}
 dirs={str(p)for n in names for p in pathlib.PurePosixPath(n).parents if str(p)!='.'}
 return names,dirs
def members(items,files):
 names,dirs=inventory(files);seen=set()
 for m in items:
  p=pathlib.PurePosixPath(m.name);n=p.as_posix()
  require(not p.is_absolute()and '..'not in p.parts and n not in seen)
  require(m.isdir()and n in dirs|{'.'}or m.isfile()and n in names)
  seen.add(n)
 require(seen==names|dirs|{'.'})
os.umask(0o077);require(os.geteuid()==0)
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28')
release=pathlib.Path('/opt/schubert-nk/current')
require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG4702'and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()==BOM)
archive=pathlib.Path(REMOTE)/'tools.private.tar';require(hashlib.sha256(archive.read_bytes()).hexdigest()==ARCHIVE)
root=pathlib.Path(GUEST);require(not os.path.lexists(root))
with tarfile.open(archive,'r:')as tar:
 members(tar.getmembers(),FILES)
 root.mkdir(mode=0o700);tar.extractall(root,filter='data')
names,dirs=inventory(FILES)
require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names)
require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_dir()}==dirs)
for p in [root,*root.rglob('*')]:
 s=p.lstat();require(not p.is_symlink()and not os.listxattr(p))
 require(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode)and s.st_nlink==1)
 os.chown(p,0,0);os.chmod(p,0o700 if p.is_dir()else 0o400)
 if p.is_file():
  with p.open('rb')as f:os.fsync(f.fileno())
for name,digest in FILES.items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest)
require(json.loads((root/'payload-sha256.json').read_bytes())==FILES)
for p in [*[root/d for d in sorted(dirs,key=lambda d:-len(pathlib.PurePosixPath(d).parts))],root,root.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'stagedFiles':len(FILES),'nestedDirectories':len(dirs),'startsStopsCredentials0':True}))
'''


def fixed():
    role.eligibility(role.BASELINE)
    value=json.loads((W/'pg4824-frozen-v1.safe.json').read_bytes())
    if not(value['actualExit']==0 and value['productionSource']==role.SOURCE and value['BOM']==role.BOM and value['beforeSha256']==role.BASELINE and len(value['phases'])==5 and all(p['actualExit']==0 for p in value['phases'])):raise ValueError('actual five current ABI phases required')
    target=W/role.TOOLS
    if {p.relative_to(target).as_posix()for p in target.rglob('*')if p.is_file()}!=set(value['fileHashes'])|{'payload-sha256.json'}:raise ValueError('full frozen inventory')
    for name,digest in value['fileHashes'].items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest()!=digest:raise ValueError('frozen tools changed')
    return value,target


def main():
    if sys.argv[1:]not in (['stage'],['verify'],['execute']):raise ValueError('exact existing20 phase')
    action=sys.argv[1];os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed source')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();proof,target=fixed()
    base=W/(SLOT+'-'+action+'-v1')
    if any(Path(str(base)+suffix).exists()for suffix in ('.requested','.private.log','.exit','.safe.json')):raise ValueError('once phase already reserved, recover original only')
    if action!='stage':
        stage=json.loads((W/(SLOT+'-stage-v1.safe.json')).read_bytes())
        if stage['actualExit']!=0 or stage['productionSource']!=role.SOURCE:raise ValueError('actual new stage first')
    if action=='execute':
        verify=json.loads((W/(SLOT+'-verify-v1.safe.json')).read_bytes())
        if verify['actualExit']!=0 or verify['productionSource']!=role.SOURCE:raise ValueError('actual new verify first')
    with management_gate(P/'current-management-critical.lock'):
        authenticate_host()
        with Path(str(base)+'.requested').open('x')as f:f.write(head+'\n');f.flush();os.fsync(f.fileno())
        started=datetime.datetime.now(datetime.timezone.utc).isoformat()
        if action=='stage':
            archive=P/(SLOT+'-v1.private.tar')
            with archive.open('xb')as f:subprocess.run(['tar','-C',str(target),'-cf','-','.'],stdout=f,check=True);f.flush();os.fsync(f.fileno())
            subprocess.run(SSH+['test ! -e '+REMOTE+' && sudo -n test ! -e '+GUEST+' && mkdir -m700 '+REMOTE],check=True)
            subprocess.run(['scp','-q',*SSH[2:-3],'-P','22222',str(archive),'ubuntu@127.0.0.1:'+REMOTE+'/tools.private.tar'],check=True)
            raw='FILES='+repr(proof['fileHashes'])+'\nBOM='+repr(role.BOM)+'\nGUEST='+repr(GUEST)+'\nREMOTE='+repr(REMOTE)+'\nARCHIVE='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\n'+STAGE
            commands=[(SSH+['sudo -n python3 -B -'],raw.encode())]
        else:
            cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG4702/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG4702/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG4702/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG4702/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
            prefix='sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" '
            commands=[(SSH+[prefix+'Pg4820'+name],None)for name in ('BootstrapArgumentTest','BootstrapExpectedTest')]
            commands.append((SSH+[prefix+'Pg4820BootstrapExisting '+action],None))
        code=0
        with Path(str(base)+'.private.log').open('xb')as log:
            for args,data in commands:
                r=subprocess.run(args,input=data,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=r.returncode
                if code:break
        with Path(str(base)+'.exit').open('x')as f:f.write(str(code)+'\n');f.flush();os.fsync(f.fileno())
        same=head==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain'])
        value={'actualExit':code,'action':action,'productionSource':role.SOURCE,'BOM':role.BOM,'operatorSource':head,'operatorUnchanged':same,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(Path(str(base)+'.private.log').read_bytes()).hexdigest(),'formalAccepted':False}
        with Path(str(base)+'.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
