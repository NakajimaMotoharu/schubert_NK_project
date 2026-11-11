"""Independent A4-01 full original4 post; same-byte source, XML/counter/CRC and URL arithmetic."""
from pathlib import Path
import datetime as dt,hashlib,json,re,subprocess,xml.etree.ElementTree as X
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence'
S=R.parent/'pgpt-runs/PG379/pg26018-saved-target-original-whole4-v1'
RAW=E/'PG26018-saved-target-original-whole4-v1';O=E/'PG26020-saved-target-independent-v1'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();m=load(RAW/'manifest.json');assert sha(RAW/'manifest.json')==sha(S/'manifest.json')
assert type(m['actualExit']) is int and m['actualExit']==0 and m['productTestsExecuted']==4
pf=load(R/m['begin']['preflight']['path']);assert sha(R/m['begin']['preflight']['path'])==m['begin']['preflight']['sha256']
assert pf['fullOriginalBodiesExactlyRestored'] is True and pf['expectedTests']==4
for p,h in pf['inputHashes'].items():
 assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+p])).hexdigest()
for p,h in pf['dependencies'].items():assert sha(Path(p))==h
for label in ['compile','unit','coverage','execinfo','classinfo']:
 stage=m['stages'][label];assert stage['actualExit']==0 and stage['timedOut'] is False and load(S/(label+'-exit.safe.json'))==stage
expected={'web005SafeGetTargetsPreservePathAndQuery','web006ExternalMalformedAndStateChangingTargetsReject','web007Utf8LimitAndUnicodeBoundariesAreExact','web008ConcurrentTargetsRemainIndependent'}
cases=[];environment=None;safe=X.Element('testsuite',name='SavedRequestTargetOriginal4',tests='4',failures='0',errors='0',skipped='0')
for name,h in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==h;root=X.parse(p).getroot()
 props={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  assert t.get('classname')=='dev.codex.schubert.nk.web.security.SavedRequestTargetTest'
  method=t.get('name').removesuffix('()');assert method in expected and not any(t.findall(tag) for tag in ['failure','error','skipped'])
  cases.append(method);X.SubElement(safe,'testcase',classname=t.get('classname'),name=t.get('name'))
  assert props['java.runtime.version'].startswith('25.0.4') and props['user.language']=='ja' and props['user.country']=='JP' and props['user.timezone']=='Asia/Tokyo'
  observed={k:props[k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']}
  if environment is None:environment=observed
  assert environment==observed
assert len(cases)==len(set(cases))==4 and set(cases)==expected
assert len(m['cases'])==4 and all(not c['nonPass'] for c in m['cases'])
root=X.parse(S/'coverage.xml').getroot();classes=root.findall('.//class');assert len(classes)==1
target='dev/codex/schubert/nk/web/security/SavedRequestTarget';assert classes[0].get('name')==target
counters={n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in root.findall('counter')}
assert all(counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
assert all(int(n.get('missed'))==0 for n in root.findall('.//counter'))
sources=root.findall('.//sourcefile');assert len(sources)==1 and sources[0].get('name')=='SavedRequestTarget.java'
index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256']
assert index[target]['sha256']==sha(S/'component/SavedRequestTarget.class')==pf['targetClassHashes'][target+'.class']
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG26018-SAVED-TARGET-ORIGINAL-WHOLE4']
positives={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4].startswith('dev/codex/schubert/nk/') and int(hit[2])>0:
  assert hit[4]==target and index[hit[4]]['crc64']==hit[1];positives[hit[4]]=hit[1]
assert set(positives)=={target}
held={'dev/codex/schubert/nk/api/messaging/inbound/TemporaryInfrastructureException','dev/codex/schubert/nk/web/logging/FingerprintKeyRing','dev/codex/schubert/nk/web/security/ResponseSnapshotCodec','dev/codex/schubert/nk/web/WebStartupException'}
initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()))
assert not any(n.rsplit('/',1)[-1] in {'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'} for n in initializers)
ref=pf['sourceContinuityAndStatic'];assert sha(R/ref['path'])==ref['sha256'];static=load(R/ref['path']);assert static['applicableViolations']==static['checkstyleFindings']==static['processingErrors']==0 and static['originalFourAssertionsUnchanged'] is True
text=(R/pf['testPaths'][0]).read_text();assert text.count('future.get(20, TimeUnit.SECONDS)')==1 and text.count('pool.awaitTermination(10, TimeUnit.SECONDS)')==1 and text.count('pool.shutdownNow();')==1
# Domain arithmetic is independent of Production URI/UTF8 implementation.
assert len(('/q?x='+'あ'*681).encode('utf-8'))==2048
assert len(('/q?x='+'a'*2043).encode('utf-8'))==2048
assert len(('/'+'a'*2048).encode('utf-8'))==2049
assert all(v in text for v in ['new int[] {2047, 2048}','for (int i = 0; i < 100; i++)','assertNull(error.getCause())','assertEquals(0, error.getSuppressed().length)','SavedRequestTarget[REDACTED]'])
O.mkdir();X.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes())
v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producer=dict(path=str((RAW/'manifest.json').relative_to(R)),sha256=sha(RAW/'manifest.json')),preflight=m['begin']['preflight'],tests=4,failures=0,errors=0,skipped=0,aborted=0,wholeFixtures=1,existingTestsRequalified=4,newUniqueTests=0,originalFourAssertionsUnchanged=True,independentUtf8ArithmeticMatched=True,coverage=counters,sourcePrograms=1,physicalClasses=1,allSourceFour100=True,finiteOwnerSitesCorrected=1,existingFutureGet20Retained=True,ownerTerminationAsserted=True,observedPositiveMainClasses=1,allObservedMainCrcMatchCurrentNormal=True,heldFourInitializations=0,singleSession=True,oldExecUnion=False,environment=environment,pmdRawFindings=5,applicableStaticViolations=0,checkstyleFindings=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,actualExternalActions=0,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=4,source=m['source'],coverage=counters,manifestSha256=sha(O/'manifest.json'))))
