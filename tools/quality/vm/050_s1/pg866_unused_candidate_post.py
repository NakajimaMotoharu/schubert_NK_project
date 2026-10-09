"""Independent placed862 receipt; preserve BUG979 original mislabelled safe sidecar."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg863_stage_candidate_v6 import source
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def payload():
    tree=ast.parse(source());body=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='PAYLOAD'for x in n.targets))
    body=body[:body.index(" root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')")]
    body+=''' root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')
 sig=pathlib.Path('/var/lib/pgpt-s1-preservation/pg862-manifest.sig')
 manifest=(root/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()=='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'
 data=json.loads(manifest);assert data['source']['commit']=='e01612fcd7f2752df5ae0836b78538fd5e87f120' and data['release']=='0.1.0-PG862' and len(data['artifacts'])==187 and len(data['migrations'])==29
 expected={r['path']:r['sha256']for r in data['artifacts']};assert len(expected)==187
 expected['RELEASE-MANIFEST.json']=hashlib.sha256(manifest).hexdigest()
 canonical=''.join(expected[n]+'  '+n+'\\n'for n in sorted(expected)).encode('ascii');assert (root/'SHA256SUMS').read_bytes()==canonical
 assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(expected)|{'SHA256SUMS'}
 for p in (root,*root.rglob('*')):
  s=p.lstat();assert not p.is_symlink() and s.st_uid==0 and s.st_gid==986
  executable=p.relative_to(root).as_posix()in ('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
  assert stat.S_IMODE(s.st_mode)==(0o750 if p.is_dir()or executable else 0o640)
  if p.is_file():assert s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==(expected[p.relative_to(root).as_posix()]if p.name!='SHA256SUMS'else hashlib.sha256(canonical).hexdigest())
 for r in data['artifacts']:assert (root/r['path']).stat().st_size==r['size']
 s=sig.lstat();assert s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1 and s.st_size==64
 assert hashlib.sha256(sig.read_bytes()).hexdigest()==SIGHASH
 subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(root/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 assert protected()==before
print('PG866_UNUSED862_POST full24-564/all32/alltrees/current832/tenStopped/signature187 PASS scopesClosed=true')
'''
    ast.parse(body);return body
if __name__=='__main__':
    os.umask(0o077);original=W/'pg863-candidate-stage-v6.safe.json';v=json.loads(original.read_bytes());assert v['actualExit']==0 and v['currentUnchanged'] and v['operatorSource']=='5243bdd11d5977658e1df210be6382bf9b75aa11'
    assert hashlib.sha256((W/'pg863-candidate-stage-v6.private.log').read_bytes()).hexdigest()==v['privateLogSha256']
    signature=P/'pg862-manifest-v1.sig';prefix='SIGHASH='+repr(hashlib.sha256(signature.read_bytes()).hexdigest())+'\n'
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    log=W/'pg866-unused862-post-v1.private.log';assert not log.exists()
    start=datetime.datetime.now(datetime.timezone.utc)
    with log.open('xb')as f:r=subprocess.run(ssh,input=(prefix+payload()).encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    result={'run':'PG866-unused862-post-v1','actualExit':r.returncode,'actualStageRun':'PG863-candidate-stage-v6','originalSafeRunMislabel':v['run'],'originalSafeSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'stageOperator':v['operatorSource'],'candidateSource':v['candidateSource'],'manifestSha256':v['manifestSha256'],'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'formalAccepted':False}
    with (W/'pg866-unused862-post-v1.safe.json').open('x')as f:json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));raise SystemExit(r.returncode)
