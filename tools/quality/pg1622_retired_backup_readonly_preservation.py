"""Exactly four retired original files from certified standalone rb QCOW.

Private preservation only. No active-disk copy, restore, VM/DB/current Backup
operation; server.info and host private keys are never included in transfer.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from pg1446_current_cold_stage import W,SSH
from lan_server import run,copy

SLOT='pg1622-retired-backup-readonly-v1'
REMOTE='/home/mini/schubert-nk-pgpt/runs/PG1622-retired-backup-v1'
RUNTIME=Path('/home/mini/codex/project1/work/toolchain/dissect-backup-readonly-20261010/runtime')

def selected_retired(before,after):
    if type(before)is not dict or type(after)is not dict:raise ValueError('retired original before/after required')
    removed=set(before)-set(after);folders=[p for p in removed if p.rsplit('/',1)[0]=='/srv/schubert-nk/backup']
    names={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'}
    if len(folders)!=1 or removed!={folders[0]}|{folders[0]+'/'+n for n in names}:raise ValueError('exact one retired five-entry closure required')
    folder=folders[0]
    if not folder.startswith('/srv/schubert-nk/backup/')or folder.endswith('.part'):raise ValueError('retired completed Backup folder required')
    old_complete={p.rsplit('/',1)[0]for p in before if p.endswith('/MANIFEST.json')and not p.rsplit('/',1)[0].endswith('.part')}
    now_complete={p.rsplit('/',1)[0]for p in after if p.endswith('/MANIFEST.json')and not p.rsplit('/',1)[0].endswith('.part')}
    if len(old_complete)!=7 or len(now_complete)!=7 or folder not in old_complete or not(old_complete-{folder}<=now_complete)or len(now_complete-old_complete)!=1:raise ValueError('seven-generation replacement contract refused')
    added=now_complete-old_complete;new_folder=next(iter(added))
    if not new_folder.endswith('-0be226b1-bbb7-43d3-aa9e-59d0bda70f9a')or set(after)-set(before)!={new_folder}|{new_folder+'/'+n for n in names}:raise ValueError('exact current new Backup entries required')
    root='/srv/schubert-nk/backup'
    for p,v in before.items():
        if p in removed:continue
        if p==root:
            now=after[p]
            if now['sha256']!=v['sha256']or now['metadata'][:6]!=v['metadata'][:6]or any(now['metadata'][i]<v['metadata'][i]for i in [6,7,8]):raise ValueError('retention root identity/counters changed')
        elif after[p]!=v:raise ValueError('retained old Backup entry changed')
    return {'folder':folder,'entries':{p:before[p]for p in sorted(removed)},'retainedCompleteFolders':sorted(now_complete)}

GUEST=r'''
import json,pathlib,hashlib
b=pathlib.Path('/var/lib/pgpt-s1-preservation')
old_raw=(b/'pg1596-current-ordinary-before-v1/before.private.json').read_bytes()
if hashlib.sha256(old_raw).hexdigest()!='6d144309d3294abb31440d523940bfd4275d3a99eab3e4ce8e0486f81a154bce':raise ValueError('fixed retired-before SHA refused')
new_raw=(b/'pg1609-native-stop-v1/after.private.json').read_bytes()
if hashlib.sha256(new_raw).hexdigest()!=AFTER_SHA:raise ValueError('fixed normal stopped current SHA refused')
old=json.loads(old_raw)['backup'];new=json.loads(new_raw)['backup'];claims={}
for p in new:
 if p.endswith('/MANIFEST.json')and not p.rsplit('/',1)[0].endswith('.part'):
  raw=pathlib.Path(p).read_bytes()
  if hashlib.sha256(raw).hexdigest()!=new[p]['sha256']:raise ValueError('retained manifest SHA refused')
  claims[p.rsplit('/',1)[0]]=json.loads(raw)['startedAt']
print(json.dumps({'before':old,'after':new,'retainedStartedAt':claims}))
'''

SERVER=r'''
import datetime,hashlib,json,os,stat,subprocess,sys,tarfile
from pathlib import Path
os.umask(0o077)
def require(v):
 if not v:raise ValueError('readonly original Backup preservation refused')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while block:=f.read(8*1024*1024):h.update(block)
 return h.hexdigest()
def identity(p):
 s=p.stat();return[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
out=Path('/home/mini/schubert-nk-pgpt/runs/PG1622-retired-backup-v1');require(out.is_dir()and not(out/'bundle').exists())
require(sha(out/'runtime.private.tar')==RUNTIME_SHA and sha(out/'expected.private.json')==EXPECTED_SHA)
runtime=out/'runtime';require(not runtime.exists());runtime.mkdir(mode=0o700)
with tarfile.open(out/'runtime.private.tar','r:')as tar:
 for member in tar.getmembers():
  p=Path(member.name);require(member.isfile()and not p.is_absolute()and '..'not in p.parts)
 tar.extractall(runtime,filter='data')
for name,digest in RUNTIME_FILES.items():require(sha(runtime/name)==digest)
sys.path.insert(0,str(runtime))
from dissect.hypervisor.disk.qcow2 import QCow2
from dissect.volume.disk import Disk
from dissect.extfs.extfs import ExtFS
expected=json.loads((out/'expected.private.json').read_bytes());folder=expected['folder'];entries=expected['entries']
base=Path('/home/mini/schubert-nk-pgpt/vm/pg1431/guest.qcow2');before=identity(base)
require(base.is_file()and not base.is_symlink()and base.stat().st_size==BASE_BYTES and sha(base)==BASE_SHA and identity(base)==before)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(base)]));require(info['format']=='qcow2'and 'backing-filename'not in info and not info.get('snapshots')and not info.get('dirty-flag'))
require(os.statvfs(out).f_bavail*os.statvfs(out).f_frsize>=10737418240+sum(v['metadata'][6]for p,v in entries.items()if p!=folder))
image=QCow2(base);require(image.fh.mode=='rb');matches=[]
try:
 for partition in Disk(image.open()).partitions:
  try:fs=ExtFS(partition.open());fs.get(folder)
  except Exception:continue
  matches.append((partition,fs))
 require(len(matches)==1);partition,fs=matches[0];dest=out/'bundle';dest.mkdir(mode=0o700);records={}
 for path,wanted in entries.items():
  node=fs.get(path);inode=node.inode;metadata=[node.inum,inode.i_uid,inode.i_gid,inode.i_mode,inode.i_links_count,node.size,node.mtime_ns,node.ctime_ns]
  require(metadata==wanted['metadata'][1:]and not node.xattr)
  if path==folder:require(stat.S_ISDIR(inode.i_mode));continue
  require(stat.S_ISREG(inode.i_mode)and 0<node.size<=128*1024*1024)
  target=dest/Path(path).name;h=hashlib.sha256();size=0
  with node.open()as source,target.open('xb')as sink:
   os.fchmod(sink.fileno(),0o600)
   while block:=source.read(131072):sink.write(block);h.update(block);size+=len(block)
   sink.flush();os.fsync(sink.fileno())
  require(size==wanted['metadata'][6]and h.hexdigest()==wanted['sha256'])
  records[target.name]={'size':size,'sha256':h.hexdigest(),'originalMetadata':wanted['metadata']}
 require(set(records)=={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'})
 old=json.loads((dest/'MANIFEST.json').read_bytes());stamp=datetime.datetime.fromisoformat(old['startedAt'].replace('Z','+00:00'))
 require(old['format']=='NKBACKUP1'and Path(folder).name==stamp.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')+'-'+old['runId'])
 current=[(datetime.datetime.fromisoformat(v.replace('Z','+00:00')),p)for p,v in expected['retainedStartedAt'].items()]
 require(len(current)==7 and(stamp,folder)==min([(stamp,folder),*current]))
 require(identity(base)==before)
finally:image.fh.close()
manifest={'scope':'PRIVATE_ORIGINAL_PRESERVATION_ONLY','folder':folder,'startedAt':old['startedAt'],'files':records,'readonlyCertifiedStandaloneBaseIdentity':before,'baseSha256':BASE_SHA,'expectedSha256':EXPECTED_SHA,'retainedSevenAndOldestRetiredVerified':True,'vmDbCurrentBackupModified0':True,'formalAccepted':False}
with(out/'manifest.private.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for p in [dest,out]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'preservedFiles':4,'preservedBytes':sum(v['size']for v in records.values()),'privateManifestSha256':sha(out/'manifest.private.json'),'exactOldInodeAndBytesMatched':True,'certifiedReadonlyBaseUnchanged':True,'retainedSevenAndOldestRetiredVerified':True,'vmDbCurrentBackupModified0':True,'formalAccepted':False}))
'''

def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean preservation operator required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    post=json.loads((W/'pg1613-current-ordinary-terminal-post-v1.safe.json').read_bytes())
    if post['actualExit']!=0 or not post['allClientAdvisoryFlock0']:raise ValueError('normal current fullpost required')
    guest='AFTER_SHA='+repr(post['proofHashes']['after.private.json']['sha256'])+'\n'+GUEST
    observed=subprocess.run(SSH+['sudo','-n','python3','-'],input=guest.encode(),capture_output=True,timeout=30)
    (out/'guest.private.err').write_bytes(observed.stderr)
    if observed.returncode:raise ValueError('private current old/new Backup metadata unavailable')
    data=json.loads(observed.stdout);expected=selected_retired(data['before'],data['after']);expected['retainedStartedAt']=data['retainedStartedAt']
    metadata=out/'expected.private.json';metadata.write_text(json.dumps(expected,sort_keys=True));files={}
    archive=out/'runtime.private.tar'
    with tarfile.open(archive,'x:')as tar:
        for p in sorted(RUNTIME.rglob('*')):
            if p.is_file()and not p.is_symlink()and '__pycache__'not in p.parts and p.suffix!='.pyc':
                name=str(p.relative_to(RUNTIME));files[name]=hashlib.sha256(p.read_bytes()).hexdigest();tar.add(p,arcname=name,recursive=False)
    proof=json.loads(Path('/home/mini/codex/project1/work/pgpt-vm/private/pg1434-lan-copy-close-v1/manifest.safe.json').read_bytes())
    raw='BASE_SHA='+repr(proof['remote']['sha256'])+'\nBASE_BYTES='+repr(proof['remote']['bytes'])+'\nEXPECTED_SHA='+repr(hashlib.sha256(metadata.read_bytes()).hexdigest())+'\nRUNTIME_SHA='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\nRUNTIME_FILES='+repr(files)+'\n'+SERVER
    from pyflakes.api import check
    if check(raw,'<actual readonly original preservation>'):raise ValueError('actual complete preservation source static gate refused')
    script=out/'server.private.py';script.write_text(raw)
    code,response=run('umask 077; test ! -e '+REMOTE+' && mkdir -m700 '+REMOTE,timeout=30)
    (out/'prepare.private.log').write_text(response)
    if code:raise ValueError('new-only private server preservation namespace refused')
    for p in [metadata,archive,script]:
        code,response=copy(p,REMOTE+'/',timeout=60);(out/(p.name+'.transfer.private.log')).write_text(response)
        if code:raise ValueError('private preservation input transfer failed')
    code,response=run('python3 -B '+REMOTE+'/server.private.py >'+REMOTE+'/result.safe.json 2>'+REMOTE+'/error.private.log; status=$?; printf "%s\\n" "$status" >'+REMOTE+'/exit; cat '+REMOTE+'/result.safe.json; exit "$status"',timeout=180)
    (out/'server.private.response').write_text(response)
    safe={'actualExit':code,'scriptSha256':hashlib.sha256(raw.encode()).hexdigest(),'rawBackupOnlyPrivate':True,'formalAccepted':False}
    if code==0:safe.update(json.loads(next(line for line in response.splitlines()if line.startswith('{'))))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return code

if __name__=='__main__':raise SystemExit(main())
