"""New-only PG489 signed candidate from completed same-source full build; no guest changes."""
import hashlib,json,pathlib,shutil,subprocess,os,zlib
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE=(WORK/'pg489-six-full-v2.source').read_text().strip()
assert len(SOURCE)==40 and set(SOURCE)<=set('0123456789abcdef')
os.umask(0o077)
assert (WORK/'pg489-six-full-v2.exit').read_text().strip()=='0'
assert (WORK/'pg489-six-full-v2.source').read_text().strip()==SOURCE
subprocess.run(['sha256sum','--check','--status',str(WORK/'pg489-six-full-v2.source-files.sha256')],cwd=ROOT,check=True)
FROZEN=WORK/'pg489-host-v2';assert FROZEN.is_dir()
gate=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG489-maintenance-terminal-full-v2/manifest.json').read_text())
assert gate['productionSource']==SOURCE and gate['actualExit']==0 and gate['allFrozenBytesMatched'] and gate['tests']>3392
for module in ['protocol','storage','bootstrap','api','web','batch']:
 source=ROOT/'src'/('schubert-nk-'+module)/'target';target=FROZEN/module
 for path in source.rglob('*'):
  if path.is_file():assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256((target/path.relative_to(source)).read_bytes()).digest()
OLD=WORK/'pg486-release-v1';NEXT=WORK/'pg489-release-v1'
assert not NEXT.exists()
raw=(OLD/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='230c6174931a8d98a34e4369086619c54cb0668e0793baf2f1efce3e0993bd1d'
data=json.loads(raw);assert len(data['artifacts'])==186
for artifact in data['artifacts']:
 p=OLD/artifact['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==artifact['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==artifact['sha256']
shutil.copytree(OLD,NEXT)
version=NEXT/'VERSION';version.write_text(version.read_text().replace('PG486','PG489').replace('2e017b4063960bfb5f2483f10510d1a6a3391a9f',SOURCE))
migration=NEXT/'db/migration/V028__retained_success_progress_seals.sql'
shutil.copyfile(ROOT/'src/schubert-nk-api/src/main/resources/db/migration'/migration.name,migration)
data['artifacts'].append({'path':migration.relative_to(NEXT).as_posix(),'size':migration.stat().st_size,'sha256':hashlib.sha256(migration.read_bytes()).hexdigest()})
profile=NEXT/'config/effective/backup-profile.json'
old_profile=profile.read_bytes();profile.write_bytes(old_profile.replace(b'\"schema\":\"027\"',b'\"schema\":\"028\"'))
assert profile.read_bytes()!=old_profile and profile.read_bytes().replace(b'\"schema\":\"028\"',b'\"schema\":\"027\"')==old_profile
assert data['versions']['schema']=='027' and len(data['migrations'])==28
def checksum(path):
 value=0
 for line in path.read_text(encoding='utf-8-sig').splitlines():
  value=zlib.crc32(line.encode('utf-8'),value)
 return value if value<2**31 else value-2**32
for entry in data['migrations']:
 if entry['type']=='SQL':
  old=OLD/'db/migration'/entry['script']
  assert old.read_bytes()==(ROOT/'src/schubert-nk-api/src/main/resources/db/migration'/entry['script']).read_bytes()
  assert checksum(old)==entry['checksum']
data['versions']['schema']='028'
data['migrations'].append({'installedRank':28,'version':'028','type':'SQL','script':migration.name,'checksum':checksum(migration),'success':True})
data['artifacts'].sort(key=lambda a:a['path'])
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
data['release']='0.1.0-PG489';data['source']['commit']=SOURCE
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
exact_artifacts();assert len(list((NEXT/'db/migration').glob('*.sql')))==28
SIG=PRIVATE/'pg489-manifest-v1.sig';assert not SIG.exists()
with (WORK/'pg489-sign-v1.private.log').open('xb') as log:
 subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(PRIVATE/'pg381-release-signing.pem'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-out',str(SIG)],stdout=log,stderr=log,check=True)
 subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(PRIVATE/'pg381-release-pin.der'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-sigfile',str(SIG)],stdout=log,stderr=log,check=True)
exact_artifacts();assert SIG.stat().st_size==64
print(json.dumps({'source':SOURCE,'manifestSha256':hashlib.sha256((NEXT/'RELEASE-MANIFEST.json').read_bytes()).hexdigest(),'artifacts':187,'sql':28,'sixFrozenByteMatches':True,'changedProjectJarPaths':changed,'signatureVerified':True,'ssc196SignedOptionsUnchangedAndNotDuplicated':True,'everyArtifactBeforeAfterSignature':True,'vmMutations':False}))
