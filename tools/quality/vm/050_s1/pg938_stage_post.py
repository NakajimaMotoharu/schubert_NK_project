"""Independent stopped stage bytes/metadata/signature witness; no activation or Unit action."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD='''
import hashlib,json,os,pathlib,stat,subprocess
root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG932');old=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==old
assert hashlib.sha256((old/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'
raw=(root/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'
v=json.loads(raw);assert v['source']['commit']=='40ef6e894573d2ffab1d1732124960f9c98d5f97'and v['release']=='0.1.0-PG932'and v['versions']['schema']=='028'
rows={r['path']:r for r in v['artifacts']};assert len(rows)==len(v['artifacts'])==187 and len(v['migrations'])==29
assert len(list((root/'db/migration').glob('*.sql')))==28
expected=set(rows)|{'RELEASE-MANIFEST.json','SHA256SUMS'}
assert {q.relative_to(root).as_posix()for q in root.rglob('*')if q.is_file()}==expected
sums={n:r['sha256']for n,r in rows.items()};sums['RELEASE-MANIFEST.json']=hashlib.sha256(raw).hexdigest()
assert (root/'SHA256SUMS').read_bytes()==''.join(sums[n]+'  '+n+'\\n'for n in sorted(sums)).encode('ascii')
before={}
for q in (root,*root.rglob('*')):
 s=q.lstat();assert not q.is_symlink()and(s.st_uid,s.st_gid)==(0,986)and not os.listxattr(q)
 executable=q.relative_to(root).as_posix()in('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
 assert(stat.S_ISDIR(s.st_mode)and stat.S_IMODE(s.st_mode)==0o750)or(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==(0o750 if executable else 0o640))
 digest=hashlib.sha256(q.read_bytes()).hexdigest()if q.is_file()else None
 if q.relative_to(root).as_posix()in rows:
  row=rows[q.relative_to(root).as_posix()];assert s.st_size==row['size']and digest==row['sha256']
 before[str(q.relative_to(root))]={'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns],'sha256':digest}
 assert q.lstat()==s
sig=pathlib.Path('/var/lib/pgpt-s1-preservation/pg932-manifest.sig');s=sig.lstat()
assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink,s.st_size)==(0,0,0o400,1,64)and not os.listxattr(sig)
subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(root/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for name,row in before.items():
 q=root/name;s=q.lstat();assert row['metadata']==[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
 assert row['sha256']==(hashlib.sha256(q.read_bytes()).hexdigest()if q.is_file()else None)
assert pathlib.Path('/opt/schubert-nk/current').readlink()==old
print(json.dumps({'actualExit':0,'candidateSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97','installedSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','artifacts':187,'schema':'028','SQL':28,'history':29,'signatureVerified':True,'currentUnchanged':True,'candidateOnly':True,'publicationNotRun':True,'nativePending':True,'metadataSnapshotSha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'signatureSha256':hashlib.sha256(sig.read_bytes()).hexdigest(),'formalAccepted':False,'rawExported':False}))
'''
if __name__=='__main__':
    os.umask(0o077);assert json.loads((W/'pg936-candidate-stage-v6.safe.json').read_bytes())['actualExit']==0
    base=W/'pg938-independent-stage-post-v1';assert not Path(str(base)+'.safe.json').exists()and not Path(str(base)+'.private.log').exists()
    cmd=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(cmd,input=PAYLOAD.encode(),capture_output=True,timeout=60)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(r.returncode)
