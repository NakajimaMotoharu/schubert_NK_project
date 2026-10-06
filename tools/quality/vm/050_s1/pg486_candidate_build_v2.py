"""New-only PG486 signed candidate from completed same-source full build; no guest changes."""
import hashlib,json,pathlib,shutil,subprocess,os
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE=(WORK/'pg486-six-full-v2.source').read_text().strip()
assert len(SOURCE)==40 and set(SOURCE)<=set('0123456789abcdef')
os.umask(0o077)
assert (WORK/'pg486-six-full-v2.exit').read_text().strip()=='0'
assert (WORK/'pg486-six-full-v2.source').read_text().strip()==SOURCE
subprocess.run(['sha256sum','--check','--status',str(WORK/'pg486-six-full-v2.source-files.sha256')],cwd=ROOT,check=True)
FROZEN=WORK/'pg486-host-v2';assert FROZEN.is_dir()
gate=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG486-maintenance-terminal-full-v2/manifest.json').read_text())
assert gate['productionSource']==SOURCE and gate['actualExit']==0 and gate['allFrozenBytesMatched'] and gate['tests']==3392
for module in ['protocol','storage','bootstrap','api','web','batch']:
 source=ROOT/'src'/('schubert-nk-'+module)/'target';target=FROZEN/module
 for path in source.rglob('*'):
  if path.is_file():assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256((target/path.relative_to(source)).read_bytes()).digest()
OLD=WORK/'pg479-release-v1';NEXT=WORK/'pg486-release-v1'
assert not NEXT.exists()
raw=(OLD/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286'
data=json.loads(raw);assert len(data['artifacts'])==186
for artifact in data['artifacts']:
 p=OLD/artifact['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==artifact['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==artifact['sha256']
shutil.copytree(OLD,NEXT)
version=NEXT/'VERSION';version.write_text(version.read_text().replace('PG479','PG486').replace('bab704707b8fd7e0dc7581c4489f0892236efe73',SOURCE))
main={'api/api.jar':'api','web/web.jar':'web','operations/batch.jar':'batch'}
changed=[]
required={'operations/bin/schubert-nk-inbox-inspector','systemd/schubert-nk-inbox-inspector.service','systemd/schubert-nk-bootstrap-admin.service'}
assert required <= {a['path'] for a in data['artifacts']}
for artifact in data['artifacts']:
 path=artifact['path'];p=NEXT/path;module=main.get(path)
 if module is None:module=next((m for m in ['protocol','storage','bootstrap','api'] if p.name=='schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'),None)
 if module is not None:
  frozen=FROZEN/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');assert frozen.is_file()
  shutil.copyfile(frozen,p);assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(frozen.read_bytes()).digest();changed.append(path)
 artifact['size']=p.stat().st_size;artifact['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
data['release']='0.1.0-PG486';data['source']['commit']=SOURCE
(NEXT/'RELEASE-MANIFEST.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
sums={a['path']:a['sha256'] for a in data['artifacts']}
sums['RELEASE-MANIFEST.json']=hashlib.sha256((NEXT/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()
(NEXT/'SHA256SUMS').write_text(''.join(sums[p]+'  '+p+'\n' for p in sorted(sums)))
def exact_artifacts():
 assert {p.relative_to(NEXT).as_posix() for p in NEXT.rglob('*') if p.is_file()}=={a['path'] for a in data['artifacts']}|{'SHA256SUMS','RELEASE-MANIFEST.json'}
 for a in data['artifacts']:
  p=NEXT/a['path'];assert p.stat().st_size==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
assert all((NEXT/p).read_bytes()==(OLD/p).read_bytes() for p in required)
assert (NEXT/'operations/bin/schubert-nk-inbox-inspector').read_text().count('sessionid=INSPECTOR-${INVOCATION_ID}-ordinary')==1
assert (NEXT/'systemd/schubert-nk-bootstrap-admin.service').read_text().count('sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary')==1
exact_artifacts();assert len(list((NEXT/'db/migration').glob('*.sql')))==27
SIG=PRIVATE/'pg486-manifest-v1.sig';assert not SIG.exists()
with (WORK/'pg486-sign-v1.private.log').open('xb') as log:
 subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(PRIVATE/'pg381-release-signing.pem'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-out',str(SIG)],stdout=log,stderr=log,check=True)
 subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(PRIVATE/'pg381-release-pin.der'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-sigfile',str(SIG)],stdout=log,stderr=log,check=True)
exact_artifacts();assert SIG.stat().st_size==64
print(json.dumps({'source':SOURCE,'manifestSha256':hashlib.sha256((NEXT/'RELEASE-MANIFEST.json').read_bytes()).hexdigest(),'artifacts':186,'sql':27,'sixFrozenByteMatches':True,'changedProjectJarPaths':changed,'signatureVerified':True,'ssc196SignedOptionsUnchangedAndNotDuplicated':True,'everyArtifactBeforeAfterSignature':True,'vmMutations':False}))
