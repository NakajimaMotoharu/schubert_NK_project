"""New-only PG479 signed candidate from completed same-source full build; no guest changes."""
import hashlib,json,pathlib,shutil,subprocess,os
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE=(WORK/'pg479-six-full-v1.source').read_text().strip()
assert len(SOURCE)==40 and set(SOURCE)<=set('0123456789abcdef')
os.umask(0o077)
assert (WORK/'pg479-six-full-v1.exit').read_text().strip()=='0'
assert (WORK/'pg479-six-full-v1.source').read_text().strip()==SOURCE
subprocess.run(['sha256sum','--check','--status',str(WORK/'pg479-six-full-v1.source-files.sha256')],cwd=ROOT,check=True)
FROZEN=WORK/'pg479-host';assert FROZEN.is_dir()
gate=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG479-maintenance-terminal-full-v1/manifest.json').read_text())
assert gate['productionSource']==SOURCE and gate['actualExit']==0 and gate['allFrozenBytesMatched'] and gate['tests']==3381
for module in ['protocol','storage','bootstrap','api','web','batch']:
 source=ROOT/'src'/('schubert-nk-'+module)/'target';target=FROZEN/module
 for path in source.rglob('*'):
  if path.is_file():assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256((target/path.relative_to(source)).read_bytes()).digest()
OLD=WORK/'pg475-release-v1';NEXT=WORK/'pg479-release-v1'
assert not NEXT.exists()
raw=(OLD/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='9183662292299cc86412c31a551bf140c8b32ccd9b2d6dcdd414b14e4bcd4806'
data=json.loads(raw);assert len(data['artifacts'])==186
for artifact in data['artifacts']:
 p=OLD/artifact['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==artifact['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==artifact['sha256']
shutil.copytree(OLD,NEXT)
version=NEXT/'VERSION';version.write_text(version.read_text().replace('PG475','PG479').replace('979c5ac3e9c28ae76363adacdf9f0736f5a59df1',SOURCE))
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
 # SSC196: only the signed isolated-PT candidate has these closed options/directories.
 if path=='operations/bin/schubert-nk-inbox-inspector':
  text=p.read_text();old="--enable-native-access=ALL-UNNAMED"
  assert text.count(old)==1
  text=text.replace(old,old+' "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=INSPECTOR-${INVOCATION_ID}-ordinary"')
  p.write_text(text);changed.append(path)
 if path=='systemd/schubert-nk-bootstrap-admin.service':
  text=p.read_text();old='ExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED'
  assert text.count(old)==1 and 'ReadWritePaths=' not in text
  text=text.replace(old,old+' -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary')
  text+='\nReadWritePaths=/run/schubert-nk/pt-coverage/ordinary-bootstrap196\n'
  p.write_text(text);changed.append(path)
 if path=='systemd/schubert-nk-inbox-inspector.service':
  text=p.read_text();assert 'ordinary-inspector196' not in text
  text+='\nReadWritePaths=/run/schubert-nk/pt-coverage/ordinary-inspector196\n'
  p.write_text(text);changed.append(path)
 artifact['size']=p.stat().st_size;artifact['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
data['release']='0.1.0-PG479';data['source']['commit']=SOURCE
(NEXT/'RELEASE-MANIFEST.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
sums={a['path']:a['sha256'] for a in data['artifacts']}
sums['RELEASE-MANIFEST.json']=hashlib.sha256((NEXT/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()
(NEXT/'SHA256SUMS').write_text(''.join(sums[p]+'  '+p+'\n' for p in sorted(sums)))
def exact_artifacts():
 assert {p.relative_to(NEXT).as_posix() for p in NEXT.rglob('*') if p.is_file()}=={a['path'] for a in data['artifacts']}|{'SHA256SUMS','RELEASE-MANIFEST.json'}
 for a in data['artifacts']:
  p=NEXT/a['path'];assert p.stat().st_size==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
assert required <= set(changed)
exact_artifacts();assert len(list((NEXT/'db/migration').glob('*.sql')))==27
SIG=PRIVATE/'pg479-manifest-v1.sig';assert not SIG.exists()
with (WORK/'pg479-sign-v1.private.log').open('xb') as log:
 subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(PRIVATE/'pg381-release-signing.pem'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-out',str(SIG)],stdout=log,stderr=log,check=True)
 subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(PRIVATE/'pg381-release-pin.der'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-sigfile',str(SIG)],stdout=log,stderr=log,check=True)
exact_artifacts();assert SIG.stat().st_size==64
print(json.dumps({'source':SOURCE,'manifestSha256':hashlib.sha256((NEXT/'RELEASE-MANIFEST.json').read_bytes()).hexdigest(),'artifacts':186,'sql':27,'sixFrozenByteMatches':True,'changedProjectJarPaths':changed,'signatureVerified':True,'everyArtifactBeforeAfterSignature':True,'vmMutations':False}))
