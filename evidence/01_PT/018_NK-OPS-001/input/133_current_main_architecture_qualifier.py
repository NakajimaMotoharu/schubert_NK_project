"""F02 static metadata only. Product jars are importer arguments, never runtime classpath."""
from pathlib import Path
import json,hashlib,subprocess,datetime,re,shutil,zipfile
import pg9666_pagination_static as c
r=Path.cwd();runs=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();spec=r/'evidence/01_PT/018_NK-OPS-001/3598_F02現4217全1844静的依存検査仕様.md';assert spec.is_file();oldpath=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG20808-current-architecture-static-v1/manifest.json';old=load(oldpath);assert sha(oldpath)=='83445800f1e503b41bce4c60bd03630d45a907baecb9117e490a437257e95926' and old['actualExit']==0
normalpath=runs/'pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';normal=load(normalpath);assert sha(normalpath)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618' and normal['source']=='4217e14083c6ecac116216e08d57f4361eb2f12d' and normal['actualExit']==0
held={'SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py','RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'};assert all(Path(n).name not in held for n in normal['begin']['inputHashes'])
for n,h in normal['begin']['inputHashes'].items():assert sha(r/n)==h
for n,h in old['toolHashes'].items():assert Path(n).name not in held and sha(Path(n))==h
observer=r/'tools/quality/architecture/ModuleDependencyAudit.java';assert sha(observer)==old['toolSourceSha256']=='108e8b3d8be2bacd0b6e0d9a158fa65212354126a34fd7181d80623fbdc6fbb1';head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':tools/quality/architecture/ModuleDependencyAudit.java'])).hexdigest()==sha(observer)
cmd=list(old['stages']['architecture']['command']);classpath=cmd[cmd.index('-cp')+1];classes=Path(classpath.split(':')[0]);assert {str(p.relative_to(classes)) for p in classes.rglob('*.class')}==set(old['toolClasses'])
for n,h in old['toolClasses'].items():assert sha(classes/n)==h
counts={};jars=normal['jars']
for name,j in jars.items():
 assert sha(Path(j['path']))==j['sha256'] and j['path'] not in classpath
 with zipfile.ZipFile(j['path']) as z:counts[name]=len([n for n in z.namelist() if n.endswith('.class') and not n.startswith('META-INF/')])
assert counts==dict(protocol=176,storage=80,bootstrap=117,api=467,web=359,batch=645) and sum(counts.values())==1844
slot=runs/'pg21694-current4217-static-architecture-v1';assert not slot.exists();slot.mkdir();c.SLOT=slot;cmd[1]='-Xlog:class+init=info:file='+str(slot/'class-init.stdout')
for i,arg in enumerate(cmd):
 if '=' in arg and arg.split('=',1)[0] in jars:module=arg.split('=',1)[0];cmd[i]=module+'='+jars[module]['path']
assert len(cmd[cmd.index('ModuleDependencyAudit')+1:])==6
assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(spec.relative_to(r))])).hexdigest()==sha(spec)
begin=dict(specification=dict(path=str(spec.relative_to(r)),sha256=sha(spec)),observerSource=head,productionMainSource=normal['source'],normalManifest=dict(path=str(normalpath),sha256=sha(normalpath)),priorStatic=dict(path=str(oldpath.relative_to(r)),sha256=sha(oldpath)),jars=jars,observerToolSourceSha256=sha(observer),observerToolClasses=old['toolClasses'],observerRuntimeClasspath=classpath,productionRuntimeClasspath=False,driverSha256=sha(Path(__file__)),moduleClassCounts=counts,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(slot/'begin.json').write_text(json.dumps(begin,indent=2)+'\n')
stage=c.step('architecture',cmd,r,timeout=120);assert stage['actualExit']==0 and not stage['timedOut'];stdout=(slot/'architecture.stdout').read_text();rules=dict((k,int(v)) for k,v in re.findall(r'^RULE\t(\w+)\t(\d+)$',stdout,re.M));assert rules=={k:0 for k in ['MODULE_EDGES','FRAMEWORK_FENCES','CONTROLLER_BOUNDARY','REPOSITORY_DIRECTION','INTERNAL_OWNER']};assert 'FINDING\t' not in stdout
imports=re.search(r'^ARCHUNIT\t1.4.2\t(\d+)\t(\d+)$',stdout,re.M);assert imports and tuple(map(int,imports.groups()))==(1844,1844);actualCounts=dict((k,int(v)) for k,v in re.findall(r'^MODULE\t(\w+)\t(\d+)$',stdout,re.M));assert actualCounts==counts;inspected=re.search(r'^INSPECTED\t(\d+)\t(\d+)$',stdout,re.M);assert inspected
initializations=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.stdout').read_text()));assert not any(n.startswith('dev/codex/schubert/nk/') for n in initializations)
pub=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21694-current4217-static-architecture-v1';assert not pub.exists();pub.mkdir();files={}
for p in slot.iterdir():
 if p.is_file():shutil.copyfile(p,pub/p.name);files[p.name]=sha(pub/p.name)
value=dict(atJST=datetime.datetime.now().astimezone().isoformat(),actualExit=0,observerSource=head,productionMainSource=normal['source'],classification='STATIC_ARCHITECTURE_METADATA_NOT_PRODUCT_PT',begin=begin,stage=stage,moduleClassCounts=counts,physicalClasses=1844,ruleFindings=rules,dependencies=int(inspected[1]),codeAccesses=int(inspected[2]),productInitializations=0,productTests=0,oldCanaryExecutions=0,oldCanaryEvidence=old['oldCanaryManifest'],oldToolCompilationRepeated=False,wholeF02Accepted=False,whole451Accepted=False,newSourceProofs=0,newAcceptance=0,formalUpdated=False,effortRate=None,unmeasuredJvmSdkSyscalls=True,files=files);(pub/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,physicalClasses=1844,findings=sum(rules.values()),dependencies=value['dependencies'],codeAccesses=value['codeAccesses'],productTests=0,manifestSha256=sha(pub/'manifest.json'))))
