"""New-only PG468 frozen full build + exact existing PG465 BOM, no VM/current mutation."""
import hashlib,json,pathlib,shutil,subprocess,os
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='bbb244e5191e68adee2f6251dfdbbba53e9b64b4'
os.umask(0o077)
assert (WORK/'pg468-six-full-v1.exit').read_text().strip()=='0'
assert (WORK/'pg468-six-full-v1.source').read_text().strip()==SOURCE
subprocess.run(['sha256sum','--check','--status',str(WORK/'pg468-six-full-v1.source-files.sha256')],cwd=ROOT,check=True)
FROZEN=WORK/'pg468-host';assert not FROZEN.exists()
for module in ['protocol','storage','bootstrap','api','web','batch']:
 source=ROOT/'src'/('schubert-nk-'+module)/'target';target=FROZEN/module
 assert source.is_dir();shutil.copytree(source,target)
 for p in source.rglob('*'):
  if p.is_file():assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((target/p.relative_to(source)).read_bytes()).digest()
OLD=WORK/'pg465-release-v2';NEXT=WORK/'pg468-release-v1'
assert not NEXT.exists() and not NEXT.is_symlink()
raw=(OLD/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e'
data=json.loads(raw);assert len(data['artifacts'])==186
for artifact in data['artifacts']:
 p=OLD/artifact['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==artifact['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==artifact['sha256']
shutil.copytree(OLD,NEXT)
module_jars={m:FROZEN/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar') for m in ['protocol','storage','bootstrap','api','web','batch']}
assert all(p.is_file() for p in module_jars.values())
main={'api/api.jar':'api','web/web.jar':'web','operations/batch.jar':'batch'}
changed=[]
for artifact in data['artifacts']:
 path=artifact['path'];p=NEXT/path
 module=main.get(path)
 if module is None:
  module=next((m for m in ['protocol','storage','bootstrap','api'] if p.name=='schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'),None)
 if module is not None:
  assert p.is_file() and not p.is_symlink();shutil.copyfile(module_jars[module],p)
  assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(module_jars[module].read_bytes()).digest();changed.append(path)
 artifact['size']=p.stat().st_size;artifact['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
data['release']='0.1.0-PG468';data['source']['commit']=SOURCE
(NEXT/'RELEASE-MANIFEST.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
version=NEXT/'VERSION';version.write_text(version.read_text().replace('PG465','PG468').replace('df9a33febf3703f0d18ac2c4ef56fd0225aac2b9',SOURCE))
(NEXT/'SHA256SUMS').write_text(''.join(a['sha256']+'  '+a['path']+'\n' for a in data['artifacts']))
assert {p.relative_to(NEXT).as_posix() for p in NEXT.rglob('*') if p.is_file()}=={a['path'] for a in data['artifacts']}|{'VERSION','SHA256SUMS','RELEASE-MANIFEST.json'}
assert len(list((NEXT/'db/migration').glob('*.sql')))==27
SIG=PRIVATE/'pg468-manifest.sig';assert not SIG.exists()
with (WORK/'pg468-sign-v1.private.log').open('xb') as log:
 subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(PRIVATE/'pg381-release-signing.pem'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-out',str(SIG)],stdout=log,stderr=log,check=True)
 subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(PRIVATE/'pg381-release-pin.der'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-sigfile',str(SIG)],stdout=log,stderr=log,check=True)
assert SIG.stat().st_size==64
print(json.dumps({'source':SOURCE,'manifestSha256':hashlib.sha256((NEXT/'RELEASE-MANIFEST.json').read_bytes()).hexdigest(),'artifacts':186,'sql':27,'sixFrozenByteMatches':True,'changedProjectJarPaths':changed,'signatureVerified':True,'vmMutations':False}))
