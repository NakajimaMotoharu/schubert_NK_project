"""Fresh six-Main compiler/NullAway snapshot; no Test source or suite/Root execution."""
import json,subprocess,tarfile,hashlib,os,datetime,sys,re
from pathlib import Path
import pg9666_pagination_static as r
root=Path.cwd();tc=root.parent/'toolchain';slotName=sys.argv[2];assert re.fullmatch(r'pg[0-9]+-[a-z0-9-]+-six-main-compile-v[0-9]+',slotName);slot=root.parent/'pgpt-runs/PG379'/slotName;assert not slot.exists();slot.mkdir();r.SLOT=slot;source=sys.argv[1];assert re.fullmatch('[0-9a-f]{40}',source);assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==source
mods=['protocol','storage','bootstrap','api','web','batch'];paths=['pom.xml','program/characterization/pom.xml']
for m in mods:paths+=['src/schubert-nk-'+m+'/pom.xml','src/schubert-nk-'+m+'/src/main']
archive=slot/'main-inputs.tar'
with archive.open('xb') as out:subprocess.run(['git','archive',source,*paths],stdout=out,check=True)
snapshot=slot/'snapshot';snapshot.mkdir()
with tarfile.open(archive) as t:
 for member in t.getmembers():
  assert not member.issym() and not member.islnk() and not member.name.startswith('/') and '..' not in Path(member.name).parts
  assert '/src/test/' not in member.name and not member.name.startswith('tools/')
 t.extractall(snapshot,filter='data')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();inputs={str(p.relative_to(snapshot)):sha(p) for p in snapshot.rglob('*') if p.is_file()};mvn=tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';cmd=[str(mvn),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(tc/'m2/repository'),'-pl',','.join('src/schubert-nk-'+m for m in mods),'-am','-Dmaven.test.skip=true','package'];begin={'source':source,'archiveSha256':sha(archive),'inputHashes':inputs,'command':cmd,'mavenSha256':sha(mvn),'testsExcludedBeforeContentRead':True,'testStatus':'NOT_COMPILED_NOT_RUN','noRootInvocation':True,'actualBackendActions':0};(slot/'begin.safe.json').write_text(json.dumps(begin,ensure_ascii=False,indent=2)+'\n')
s=r.step('compile',cmd,snapshot,timeout=600);outputs={}
if s['actualExit']==0:
 for m in mods:
  p=snapshot/('src/schubert-nk-'+m+'/target/schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');assert p.is_file();outputs[m]={'path':str(p),'sha256':sha(p)}
assert all(sha(snapshot/p)==h for p,h in inputs.items());manifest={'actualExit':s['actualExit'],'source':source,'begin':begin,'terminal':s,'jars':outputs,'sourceInputsUnchanged':True,'testsExecuted':0,'testStatus':'SKIPPED_BY_EXPLICIT_MANUFACTURING_BUILD_NOT_PT_PASS','nullAwayConfiguration':'Unchanged inherited default-compile ErrorProne2.50.0/NullAway0.14.1/JSpecifyMode/JSpecifyJDKModels; no proc-none or skip flags for Main','whole451Accepted':False,'formalUpdated':False};(slot/'manifest.safe.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':s['actualExit'],'manifestSha256':sha(slot/'manifest.safe.json'),'jars':list(outputs),'testsExecuted':0}));raise SystemExit(s['actualExit'])
