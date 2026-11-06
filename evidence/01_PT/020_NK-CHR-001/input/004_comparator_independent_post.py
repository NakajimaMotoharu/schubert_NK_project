"""Original tool run source/CRC/XML qualification; never runs a real CHR or Java process."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,re,datetime
import xml.etree.ElementTree as E
r=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());source='e7a8fe792ffe6b85a80a5fd897bd1dfe415e230f';normalSource='087e81a679a576721d8b6d6124fdd881ae9192e5';pub=Path('evidence/01_PT/020_NK-CHR-001/evidence/PG21102-comparator-selected-ten-v1');m=load(pub/'manifest.json');assert sha(pub/'manifest.json')=='af618355e6b71eed4e33d92b8970c7db5e7c0f434d08d8c9f6c86ff46beada06';assert m['actualExit']==0 and m['source']==source and m['normalSource']==normalSource and m['tests']==10 and m['newMethods']==2 and m['requalifiedExistingMethods']==8 and all(m[k]==0 for k in ['failures','errors','skipped']);assert m['realBaselineAccess'] is False and m['realChrExecution'] is False and m['oldExecUnion'] is False and m['manualCoverageExclusions']==[]
for name,h in m['files'].items():assert '/' not in name and sha(pub/name)==h
for name,h in m['inputHashes'].items():assert sha(name)==h==hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest()
for key in ['producerGitArtifact','verifierGitArtifact']:
 g=m[key];assert hashlib.sha256(subprocess.check_output(['git','show',g['source']+':'+g['path']])).hexdigest()==g['sha256']
assert m['producerGitArtifact']['source']==source and m['driverSha256']==m['producerGitArtifact']['sha256']
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.json');assert sha(slot/'manifest.json')==m['originalManifest']['sha256'] and raw['actualExit']==0 and raw['begin']['inputHashes']==m['inputHashes'] and raw['begin']['source']==source;assert raw['begin']['newMethods']==2 and raw['begin']['existingMethodsSourceRequalification']==8
for key,s in raw['stages'].items():assert s['actualExit']==0 and not s['timedOut'] and sha(slot/(key+'.stdout'))==s['stdoutSha256'] and sha(slot/(key+'.stderr'))==s['stderrSha256']
actual=[];environment=[]
for name,h in m['originalXmlPins'].items():
 assert sha(name)==h;tree=E.parse(name).getroot();assert all(int(tree.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for case in tree.findall('testcase'):
  assert not any(case.findall(k) for k in ['failure','error','skipped']);actual.append((case.get('classname'),case.get('name').removesuffix('()')))
 props={x.get('name'):x.get('value') for x in tree.findall('properties/property')};assert props['java.io.tmpdir']==str(slot/'tmp');assert props['chr.unitProjectRoot']==str(slot.parent/'pg21110-comparator-selected-ten-final-compile-v1/design-only');environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
assert sorted(actual)==sorted(map(tuple,m['selectedMethods'])) and len(actual)==len(set(actual))==10
spec=Path('evidence/01_PT/020_NK-CHR-001/018_比較工具自己所有JSON単体仕様.md').read_text();pairs=re.findall(r'\|(PT-CHR-CMP\d{3})\|(\w+)\.(\w+)\|',spec);assert len(pairs)==10 and {(c,n) for _,c,n in pairs}=={(c.rsplit('.',1)[1],n) for c,n in actual};assert sum('EmptyInputTest' in c for c,n in actual)==2 and sum(c.endswith('.ArtifactComparatorTest') for c,n in actual)==8 and not any(c.endswith('.CorrelatedLogEvidenceValidatorTest') for c,n in actual)
normal=load(slot.parent/'pg21088-characterization-tool-original-main-compile-v1/manifest.safe.json');assert normal['source']==normalSource and normal['actualExit']==0 and len(normal['physicalHashes'])==10
for name,h in normal['begin']['inputHashes'].items():assert sha(name)==h
jar=normal['jar'];assert sha(jar['path'])==jar['sha256']
with zipfile.ZipFile(jar['path']) as z:
 for n,h in m['physicalHashes'].items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==h
assert len(m['physicalHashes'])==2;coverage={c.get('name'):{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')};assert coverage==m['coverage'];four={k:sum(cs.get(k,{}).get('covered',0) for cs in coverage.values()) for k in ['LINE','METHOD','CLASS','BRANCH']};assert four==dict(LINE=214,METHOD=28,CLASS=2,BRANCH=96) and all(v['missed']==0 for cs in coverage.values() for v in cs.values())
ex=(slot/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+m['session']+'"' in ex
for name,crc in m['classIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(name)+r'$',ex,re.M)
static=Path('evidence/01_PT/020_NK-CHR-001/evidence/PG21112-comparator-ten-final-static-v1/manifest.json');s=load(static);assert s['inputHashes']==m['inputHashes'] and s['pmdRaw']==9 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==s['spotbugs']==0 and all(x['applicable'] is False and x['reason'] for x in s['classification'])
# Same pinned Console startup and JDK metadata proof; not a statement that all SDK syscalls are zero.
cmd=raw['stages']['unit']['command'];console=cmd[cmd.index('-jar')+1];sdk=load('evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json');assert sha(console)==sdk['consoleSha256']==raw['begin']['consoleSha256'];assert sha(r.parent/'toolchain/jdk-25.0.4/lib/modules')==sdk['jdkModulesSha256'];assert '--scan-classpath' not in cmd and not any(x.startswith('jdbc:') for x in cmd)
providers={}
for p in [Path(v) for v in raw['begin']['dependencies']]+[Path(console)]:
 assert sha(p)==(raw['begin']['consoleSha256'] if p==Path(console) else raw['begin']['dependencies'][str(p)])
 with zipfile.ZipFile(p) as z:providers[str(p)]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver' or n.startswith(('org/postgresql/','com/microsoft/playwright/'))]
assert all(not v for v in providers.values());assert not any('postgresql' in n or 'playwright' in n for n in providers)
for name,h in m['inputHashes'].items():
 if '/tests/resources/cases/' in name:
  owned=slot.parent/'pg21110-comparator-selected-ten-final-compile-v1/design-only'/name;assert sha(owned)==h
out=Path('evidence/01_PT/020_NK-CHR-001/evidence/PG21116-comparator-independent-post-v1');assert not out.exists();out.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,normalSource=normalSource,productionCoreMain=m['productionCoreMain'],originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),tests=10,newMethods=2,requalifiedExistingMethods=8,sourceTestIds=pairs,fourCounters=four,missed=0,physical=2,environment=environment,staticPost=dict(path=str(static),sha256=sha(static)),fixedConsoleJdkReview=dict(path='evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json',sha256=sha('evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json')),driverProviderEntries=providers,productTestsReexecuted=0,realBaselineReadOrWritten=False,realChrExecution=False,newAcceptance=0,formalUpdated=False,effortRate=None,checkerSha256=sha(__file__),checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip());(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=10,newMethods=2,requalifiedExisting=8,manifestSha256=sha(out/'manifest.json'))))
