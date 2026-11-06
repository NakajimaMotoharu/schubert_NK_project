"""Independent read-only qualification/repack of the already-ended fixed local template run."""
from pathlib import Path
import json,hashlib,subprocess,re,zipfile,shutil,datetime
import xml.etree.ElementTree as E
R=Path.cwd();W=R.parent/'pgpt-runs/PG379';SOURCE='efa3bd7b4d536cc83f08b160cde2f44ceb57f9fd';CORE='d8ff9efb16a7da1b073bdf9770487e3e6415b636';U=W/'pg20314-list-template-resource-twelve-unit-v1';P=W/'pg20308-list-template-resource-compile-v1';OLD=R/'evidence/01_PT/016_NK-WEB-002/evidence/PG20314-list-template-resource-twelve-v1/manifest.json';O=R/'evidence/01_PT/016_NK-WEB-002/evidence/PG20318-list-template-resource-independent-qualified-v1';TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ListTemplateResourcePortTest.java';CLS='dev.codex.schubert.nk.web.view.ListTemplateResourcePortTest';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());gh=lambda p:hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+p])).hexdigest()
assert not O.exists();um=load(U/'manifest.json');assert sha(U/'manifest.json')=='7738a45b64356b147bfe4e3e4209d5ab878d9f899feb01bff44816869f0d782b' and um['actualExit']==0;begin=um['begin'];assert begin==load(U/'begin.json') and begin['source']==SOURCE and begin['productionCoreMain']==CORE and begin['productionJavaClasspath'] is False;assert sha(P/'manifest.json')==begin['prepareManifestSha256']=='99ec1c85ee34e0c4eb5c04beac4dbc21da13d21fc44ceef7eceb248929d4d726';pm=load(P/'manifest.json');assert pm['inputHashes']==begin['inputHashes'] and pm['driverSha256']==begin['driverSha256']
for name,h in begin['inputHashes'].items():
 assert not Path(name).is_absolute() and '..' not in Path(name).parts and gh(name)==h
 if name!= 'evidence/01_PT/016_NK-WEB-002/input/002_list_template_resource_qualifier.py':assert sha(R/name)==h
for name,h in begin['dependencies'].items():assert sha(name)==h and '/toolchain/m2/repository/' in name
for name,h in pm['classes'].items():assert sha(P/'classes'/name)==h
for name,h in pm['resourceHashes'].items():assert sha(P/'resources'/name)==h==sha(R/'src/schubert-nk-web/src/main/resources'/name)
normal=W/'pg20112-log-tx-six-main-compile-v1/manifest.safe.json';nm=load(normal);assert sha(normal)==begin['normalManifestSha256'] and nm['source']==CORE and nm['actualExit']==0;jar=nm['jars']['web'];assert sha(jar['path'])==jar['sha256']
with zipfile.ZipFile(jar['path']) as z:
 for name,h in pm['resourceHashes'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
stage=um['stage'];assert stage==load(U/'unit-exit.safe.json') and stage['actualExit']==0 and not stage['timedOut'] and stage['startUTC']<=stage['endUTC']
for suffix in ['stdout','stderr']:assert sha(U/('unit.'+suffix))==stage[suffix+'Sha256']
cmd=stage['command'];cp=cmd[cmd.index('--class-path')+1].split(':');assert cp[:2]==[str(P/'classes'),str(P/'resources')] and all('/toolchain/m2/repository/' in x or x.endswith('junit-platform-console-standalone-1.13.4.jar') for x in cp[2:]);assert cmd[cmd.index('--select-class')+1]==CLS and cmd.count('--select-class')==1;assert not any(x.startswith(('-javaagent:','--enable-native-access')) for x in cmd)
expected=set(re.findall(r'@Test\s+void\s+(\w+)\(', (R/TEST).read_text()));cases=[];xmlpins={};env=[]
for p in (U/'xml').glob('TEST-*.xml'):
 xmlpins[str(p)]=sha(p);root=E.parse(p).getroot();props={x.get('name'):x.get('value') for x in root.findall('properties/property')};assert props['java.version']=='25.0.4' and props['java.io.tmpdir']==str(U/'tmp')
 env.append({k:props[k] for k in ['os.name','os.arch','os.version','java.version','java.vendor','java.runtime.version'] if k in props})
 for c in root.findall('testcase'):assert c.get('classname')==CLS and not any(c.findall(k) for k in ['failure','error','skipped']);cases.append(c.get('name').removesuffix('()'))
assert len(cases)==12 and set(cases)==expected and len(set(cases))==12;init=set(re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()));assert not any(x.startswith('dev/codex/schubert/nk/') and not x.startswith(CLS.replace('.','/')) for x in init)
forbidden=('org/springframework/context/annotation/AnnotationConfig','org/springframework/context/support/GenericApplicationContext','org/springframework/beans/factory/support/DefaultListableBeanFactory','org/apache/activemq/','org/apache/catalina/','io/netty/','com/zaxxer/','io/micrometer/');assert not any(x.startswith(forbidden) for x in init)
old=load(OLD);assert sha(OLD)=='1736ee797e70abbac3e6f5aeea61ab769f49bf5229e2e4c213de32fd99ce400f';assert old['files']['manifest.json']==sha(U/'manifest.json')!=sha(OLD)
for name,h in old['files'].items():
 if name!='manifest.json':assert sha(OLD.parent/name)==h
html=sorted((U/'output').glob('*.html'));assert len(html)==19 and {p.name.split('-')[0].split('.')[0] for p in html}=={'LDOM'+str(i).zfill(3) for i in range(1,13)}
# Metadata regression: destination collision and self-reference are rejected, actual tampering differs.
pairs=[(U/'manifest.json','original-manifest.json'),(U/'begin.json','begin.json'),(U/'unit.stdout','unit.stdout'),(U/'unit.stderr','unit.stderr'),(U/'unit-begin.safe.json','unit-begin.safe.json'),(U/'unit-process.safe.json','unit-process.safe.json'),(U/'unit-exit.safe.json','unit-exit.safe.json')]+[(p,'output/'+p.name) for p in html];names=[name for _,name in pairs];assert len(names)==len(set(names)) and 'manifest.json' not in names
bad=[x for x in names if x=='manifest.json']+['manifest.json'];assert 'manifest.json' in bad;assert hashlib.sha256(b'original').digest()!=hashlib.sha256(b'changed').digest()
O.mkdir();files={}
for src,name in pairs:
 dest=O/name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(src,dest);files[name]=sha(dest)
for name,h in files.items():assert sha(O/name)==h
out=dict(actualExit=0,source=SOURCE,productionCoreMain=CORE,tests=12,failures=0,errors=0,skipped=0,aborted=0,testMethods=sorted(cases),inputHashes=begin['inputHashes'],producerDriverSha256=begin['driverSha256'],verifierSha256=sha(__file__),verifierSource='TO_BE_FIXED_BEFORE_EXECUTION',originalManifest=dict(path=str(U/'manifest.json'),sha256=sha(U/'manifest.json')),originalXmlPins=xmlpins,environment=env,resourceHashes=pm['resourceHashes'],normalWebJarSha256=jar['sha256'],snapshotCount=19,files=files,oldPublicQualification=dict(path=str(OLD.relative_to(R)),sha256=sha(OLD),status='UNACCEPTED_BASENAME_COLLISION_PRESERVED'),metadataChecks=dict(uniqueDestinations=True,noQualifiedManifestSelfReference=True,actualFilesHashMatched=True,oldSelfReferenceRejected=True),productionJavaClasspath=False,applicationInitializations=[],forbiddenBusinessInitializations=[],javaCoverage=None,javaCoverageReason='HTML resource-only, no Production Java on classpath or initialized; no exclusions/100 invention/old exec union',formalUpdated=False,newAccepted=0,fullMvcOrBrowserAccepted=False,productTestsReexecuted=0,bug='BUG-2327',horizontal='YKT-2072',atJST=datetime.datetime.now().astimezone().isoformat())
# A separate verifier source is pinned now; producer source remains the original Unit source.
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();relative=str(Path(__file__).resolve().relative_to(R));assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+relative])).hexdigest()==sha(__file__);out['verifierSource']=head;(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');assert all(sha(O/n)==h for n,h in out['files'].items());print(dict(postExit=0,tests=12,snapshots=19,unitRerun=False,manifestSha256=sha(O/'manifest.json')))
