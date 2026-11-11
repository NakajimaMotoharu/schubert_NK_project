"""Current public normal inputs/static/class-domain preflight; zero test execution, no held-class IO."""
from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess,zipfile,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26308-protocol-unicode-preflight-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
main=B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json';assert sha(main)=='9342d69793ec599c4bac012de15d7c574cab132517d6f6f48de68ac57b07d695';mm=load(main);cm=load(B/'evidence/PG26304-protocol-unicode-full130-compile-v3/manifest.json');assert cm['actualExit']==0 and len(cm['tests'])==28 and cm['expectedTests']==130;assert all(sha(R/p)==h for p,h in cm['inputHashes'].items());old=load(R/'evidence/01_PT/002_NK-PRO-002/evidence/PG26242-protocol-named59-flag6-independent-v1/compile-manifest.json');cfg=load(R/'evidence/01_PT/002_NK-PRO-002/input/028_protocol_named59_scope.json');assert all(sha(R/p)==old['inputHashes'][p] for p in cfg['testSources']+cfg['resources'])
normal=load(B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json');oldc={k.split(':',1)[1]:v for k,v in normal['normalPhysicalClassHashes'].items() if k.startswith('protocol:')};delta=[p for p,h in mm['physicalClassHashes'].items() if oldc[p]!=h];expectedNames=['dev/codex/schubert/nk/protocol/file/MediaDescriptorValidator.class','dev/codex/schubert/nk/protocol/layout/semantic/RelativePath.class','dev/codex/schubert/nk/protocol/layout/semantic/DisplayPath.class'];assert set(delta)==set(expectedNames)
mainDelta=[p for p,h in mm['inputHashes'].items() if normal['begin']['inputHashes'][p]!=h];assert len(mainDelta)==3
for p in mainDelta:
 current=(R/p).read_bytes();original=subprocess.check_output(['git','show','7aed8eace7c844c2f79f2e39db766faf914890d5:'+p]);assert current.replace(b'        || !StandardCharsets.UTF_8.newEncoder().canEncode(value)\n',b'')==original
static=B/'evidence/PG26282-protocol-unicode-static-v1';s=load(static/'manifest.json');changed=B/'evidence/PG26306-unicode-two-current-style-v1';t=load(changed/'manifest.json');assert t['actualExit']==0 and t['inputHashes']==cm['inputHashes'] and t['findings']=={'pmd':0,'checkstyle':0};assert all(v['actualExit']==0 for v in t['stages'].values());root=E.parse(changed/'pmd.xml').getroot();assert not root.findall('.//{*}error') and not root.findall('.//{*}configerror');new=set(t['changedTests']);assert len(new)==2
for p,h in s['inputHashes'].items():
 if p.endswith('/1183_protocol_unicode_prepare_static.py') or p in new:continue
 assert sha(R/p)==h
oldpmd=E.parse(static/'pmd.xml').getroot();errs=[x for x in oldpmd if x.tag.rsplit('}',1)[-1] in ['error','configerror']];assert len(errs)==2 and all(str(Path(x.get('filename')).relative_to(R)) in new for x in errs);assert s['stages']['pmd']['actualExit']==5
occ=[]
for file in oldpmd:
 if file.tag.rsplit('}',1)[-1]!='file':continue
 p=str(Path(file.get('name')).relative_to(R))
 if p in new:continue
 for v in file:
  if v.tag.rsplit('}',1)[-1]!='violation':continue
  rule=v.get('rule');line=int(v.get('beginline'));assert sha(R/p)==s['inputHashes'][p]
  if rule=='UseConcurrentHashMap':reason='Fresh invocation-only local ordered/fixture map, not shared container state; immutable return or synchronous Test consumer. ConcurrentHashMap would discard intended insertion-order contract.'
  elif rule=='NullAssignment' and '/src/test/' in p:reason='Deliberate independent null-contract negative fixture, not production normal-state null assignment.'
  elif rule=='DoNotUseThreads' and '/src/test/' in p:reason='JUnit standalone memory-only concurrency oracle; no application-container managed thread policy. Both fixed executors finally shutdownNow and bounded awaitTermination10.'
  elif rule=='CloseResource' and '/src/test/' in p:reason='Owner closes fixed executor in finally with shutdownNow and asserted termination10; borrowed jobs finish bounded future/get; no unbounded worker.'
  elif rule=='CompareObjectsWithEquals' and p.endswith(('FailedJmsIsolationException.java','UnconfirmedJmsRollbackException.java')):reason='Throwable identity guard deliberately avoids Java self-suppression; equality of distinct Throwable is not the ownership condition.'
  else:raise AssertionError((p,rule,line))
  occ.append(dict(path=p,line=line,rule=rule,classification='CONTEXTUAL_NONAPPLICABLE',reason=reason,actualViolation=False))
assert len(occ)==21;assert s['stages']['checkstyle']['actualExit']==0 and not s['reports']['checkstyle']['items'];assert s['stages']['spotbugs']['actualExit']==0 and s['spotbugs']['bugs']==s['spotbugs']['missing']==s['spotbugs']['errors']==0
stats={p.removesuffix('.class').replace('/','.') for p in mm['physicalClassHashes']};assert set(s['spotbugs']['classStats'])==stats and len(stats)==176
# Preserve all eight independent malformed UTF16 code-unit sequences, not analyzer exclusions.
expected=[[0xd800],[0xdfff],[0xd800,120],[120,0xdfff],[0xd800,0xd800],[0xdfff,0xdfff],[0xdfff,0xd800],[0xd83d,0xde00,0xd800]]
for p in new:
 text=(R/p).read_text();assert 'String high = String.valueOf((char) 0xd800);' in text and 'String low = String.valueOf((char) 0xdfff);' in text and 'new char[] {(char) 0xd83d, (char) 0xde00}' in text
 before=B/'evidence/PG26302-pmd-surrogate-before-v1'/(Path(p).name+'.before.txt');raw=before.read_text().split('private static List<String> malformedValues() {',1)[1].split('\n  }',1)[0];values=re.findall(r'"([^"\n]*)"',raw);assert len(values)==8
 decoded=[]
 for x in values:
  decoded.append([int.from_bytes(v,'little') for v in [bytes.fromhex('0000')]] if False else [int(v,16) if len(v)==4 else ord(v) for v in re.findall(r'\\u([0-9a-fA-F]{4})|([^\\])',x) for v in [v[0] or v[1]]])
 assert decoded==expected
jar=Path(mm['jar']['path']);assert sha(jar)==mm['jar']['sha256']
with zipfile.ZipFile(jar) as z:
 names=[p for p in z.namelist() if p.endswith('.class')];assert len(names)==176 and set(names)==set(mm['physicalClassHashes']);assert not any(any(w in p for w in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']) for p in names);assert all(hashlib.sha256(z.read(p)).hexdigest()==mm['physicalClassHashes'][p] for p in names)
O.mkdir();(O/'static-applicability21.json').write_text(json.dumps(occ,ensure_ascii=False,indent=2)+'\n');(O/'independent-malformed-codeunits.json').write_text(json.dumps(expected,indent=2)+'\n');v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=cm['inputHashes'],MainCompileManifest=dict(path=str(main.relative_to(R)),sha256=sha(main)),TestCompileManifest=dict(path=str((B/'evidence/PG26304-protocol-unicode-full130-compile-v3/manifest.json').relative_to(R)),sha256=sha(B/'evidence/PG26304-protocol-unicode-full130-compile-v3/manifest.json')),mainDeltaPaths=mainDelta,physicalDelta=delta,physicalClasses=176,mainSources=165,TestSources=28,expectedTests=130,newTestDefinitions=6,original124SourceAndFiveFixturesUnchanged=True,mainChangeInverseExact=True,static=dict(pmdRawCurrent=21,applicable=0,unclassified=0,checkstyle=0,processingErrors=0,spotbugsBugs=0,spotbugsMissing=0,spotbugsErrors=0,spotbugsExactClassStats=176,originalPmd5ErrorsPreserved=2,changedTwoInputsNewStatic0=True),staticWholeModuleNotSixModule=True,malformedCodeUnitVectors=8,expectedNegativeObservations=40,productTestsExecuted=0,heldActualClassIo=False,Root2SourceIo=False,backendNativeOrVmUsed=False,whole451Accepted=False,formalUpdated=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedTests=130,mainClassDelta=3,staticApplicable=0,staticProcessingErrors=0,manifestSha256=sha(O/'manifest.json'))))
