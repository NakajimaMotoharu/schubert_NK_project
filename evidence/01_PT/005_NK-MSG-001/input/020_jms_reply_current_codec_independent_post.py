"""Verify the original seven-run; JAR metadata tools never initialize Product classes."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess, zipfile
import xml.etree.ElementTree as ET
import pg9666_pagination_static as c
r=Path.cwd();runs=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21824-jms-reply-current-codec-seven-v1/manifest.json';assert sha(p)=='e1e108aa4bd43cea0a131debbaf910063ca812c268bee1d64a665e4460659a55';m=load(p);ctx=m['context']
assert m['actualExit']==m['failures']==m['errors']==m['skipped']==m['aborted']==0 and m['tests']==m['requalifiedExistingInvocations']==7 and m['newMethods']==0
for n,h in m['files'].items():assert sha(p.parent/n)==h
for n,h in ctx['inputHashes'].items():
 assert sha(r/n)==h
 assert hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n])).hexdigest()==h
for n,h in ctx['runtimeInputs'].items():assert sha(Path(n))==h
assert m['unitTerminal']['actualExit']==0 and m['unitTerminal']['contextSha256']==m['files']['compile-context.safe.json']
assert m['static']['rawPmdExit']==4 and m['static']['applicableViolations']==0 and m['static']['checkstyleExit']==0
assert [(a['rule'],a['line']) for a in m['static']['findings']]==[('UseConcurrentHashMap',216),('UseConcurrentHashMap',233),('UseConcurrentHashMap',239),('UseProperClassLoader',256),('CompareObjectsWithEquals',298)]
safe=ET.parse(p.parent/'testcases.safe.xml');actual={(a.get('classname'),a.get('name')) for a in safe.getroot().iter('testcase')};assert actual=={tuple(x) for x in m['selectedTestMethods']} and {n for _,n in actual}==set(ctx['expectedMethods']) and len(actual)==7
for n,h in m['originalXmlPins'].items():assert sha(Path(n))==h
normalp=Path(ctx['normalManifest']['path']);assert sha(normalp)==ctx['normalManifest']['sha256'];normal=load(normalp);assert normal['actualExit']==0 and normal['source']==ctx['productionCoreMain']
web,protocol=ctx['jars']['web'],ctx['jars']['protocol'];assert web==normal['jars']['web'] and protocol==normal['jars']['protocol']
for n,h in ctx['physicalHashes'].items():assert normal['normalPhysicalClassHashes']['web:'+n+'.class']==h
assert not any(s in ctx['classpath'] for s in ['schubert-nk-api-','schubert-nk-storage-','schubert-nk-bootstrap-','schubert-nk-batch-','postgresql-','artemis-server-'])
forbidden={'dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'}
init=set(re.findall(r"Initializing '([^']+)",(p.parent/'unit-class-init.stdout').read_text()));assert not (init & forbidden)
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest()==sha(Path(__file__))
slot=runs/'pg21828-jms-reply-current-codec-independent-v1';assert not slot.exists();slot.mkdir();c.SLOT=slot
java=str(r.parent/'toolchain/jdk-25.0.4/bin/java');cli=str(r.parent/'toolchain/org.jacoco.cli-0.8.15-nodeps.jar');jars=[web['path'],protocol['path']]
# These JARs are analyzer arguments, never the tool runtime classpath. No class is extracted.
stages={}
stages['normal-classinfo']=c.step('normal-classinfo',[java,'-Xlog:class+init=info:file='+str(slot/'classinfo-init.stdout'),'-jar',cli,'classinfo',*jars],r,timeout=60)
stages['dependency-report']=c.step('dependency-report',[java,'-Xlog:class+init=info:file='+str(slot/'report-init.stdout'),'-jar',cli,'report',str(p.parent/'jacoco.exec'),'--classfiles',web['path'],'--classfiles',protocol['path'],'--xml',str(slot/'dependency-coverage.xml')],r,timeout=60)
assert all(s['actualExit']==0 and not s['timedOut'] for s in stages.values())
for name in ['classinfo-init.stdout','report-init.stdout']:
 assert not any(n.startswith('dev/codex/schubert/nk/') for n in re.findall(r"Initializing '([^']+)",(slot/name).read_text()))
ids={n:i for i,n in re.findall(r'(?:class|interface|enum|record) 0x([0-9a-f]{16})\s+(\S+)',(slot/'normal-classinfo.stdout').read_text())}
physical={}
for module,jar in [('web',web),('protocol',protocol)]:
 with zipfile.ZipFile(jar['path']) as z:
  for name in z.namelist():
   if name.endswith('.class') and not name.startswith('META-INF/'):
    cls=name[:-6];h=hashlib.sha256(z.read(name)).hexdigest();assert normal['normalPhysicalClassHashes'][module+':'+name]==h;assert cls not in physical;physical[cls]=h
assert len(physical)==535 and set(ids)==set(physical)
execs={n:dict(id=i,hits=int(h),probes=int(v)) for i,h,v,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',(p.parent/'execinfo.stdout').read_text(),re.M)}
compiled=runs/'pg21818-jms-reply-current-codec-compile-v1/test-classes'
test_names={str(q.relative_to(compiled))[:-6] for q in compiled.rglob('*.class')}
unknown={n for n in execs if n.startswith('dev/codex/schubert/nk/') and n not in physical and n not in test_names};assert not unknown
positive={n:d for n,d in execs.items() if n in physical and d['hits']>0};assert positive
for n,d in positive.items():assert d['id']==ids[n]
assert not any(execs.get(n,{}).get('hits',0)>0 for n in forbidden)
tree=ET.parse(slot/'dependency-coverage.xml');assert [s.get('id') for s in tree.getroot().findall('sessioninfo')]==[ctx['session']]
methods={};partial={}
for node in tree.findall('.//class'):
 name=node.get('name');called=[]
 for method in node.findall('method'):
  counter=next((a for a in method.findall('counter') if a.get('type')=='METHOD'),None)
  if counter is not None and int(counter.get('covered'))>0:called.append(dict(name=method.get('name'),descriptor=method.get('desc')))
 if called:
  assert name in positive;methods[name]=called
  partial[name]={a.get('type'):dict(covered=int(a.get('covered')),missed=int(a.get('missed'))) for a in node.findall('counter')}
assert all(n in methods for n in m['coverage'])
for n,cs in m['coverage'].items():assert partial[n]==cs
out=r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21828-jms-reply-current-codec-independent-post-v1';assert not out.exists();out.mkdir();files={}
for q in slot.iterdir():
 if q.is_file():
  data=q.read_bytes();(out/q.name).write_bytes(data);files[q.name]=sha(out/q.name)
witness=dict(normalMetadataClasses=535,normalJarHashes=dict(web=web['sha256'],protocol=protocol['sha256']),positiveMainClasses=positive,reportedCoveredMethods=methods,reportedPartialCounters=partial,positiveClassesWithoutReportedMethod=sorted(set(positive)-set(methods)),wholeDependencyCoverageAccepted=False,oldExecUnion=False,heldMainInitialized=[],heldMainExecutedProbes=0,productClassExtractionPerformed=False,analyzerProductInitializations=0)
(out/'dependency-witness.json').write_text(json.dumps(witness,ensure_ascii=False,indent=2)+'\n');files['dependency-witness.json']=sha(out/'dependency-witness.json')
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],checkerSource=head,checkerSha256=sha(Path(__file__)),productionCoreMain=m['productionCoreMain'],original=dict(path=str(p.relative_to(r)),sha256=sha(p)),tests=7,newMethods=0,requalifiedExistingInvocations=7,newSourceProofs=0,newAcceptance=0,coverage=m['coverage'],naturalZeroBranchClasses=m['naturalZeroBranchClasses'],normalMetadataClasses=535,positiveMainClassCount=len(positive),reportedMethodCount=sum(map(len,methods.values())),dependencyWitness=dict(path='dependency-witness.json',sha256=files['dependency-witness.json']),stages=stages,files=files,heldInitAndProbeHits=0,analyzerProductInitializations=0,wholeDependencyCoverageAccepted=False,whole451Accepted=False,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=7,newMethods=0,normalMetadataClasses=535,positiveMainClasses=len(positive),reportedMethods=sum(map(len,methods.values())),manifestSha256=sha(out/'manifest.json'))))
