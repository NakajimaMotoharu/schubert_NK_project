"""Fail-closed complete Protocol scope/source/static evidence before original119 execution."""
from pathlib import Path
import json,hashlib,re,zipfile,datetime,subprocess
R=Path.cwd();B=R/'evidence/01_PT/002_NK-PRO-002';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/017_protocol_whole120_scope.json');pre=RUNS/cfg['compileSlot'];sta=RUNS/cfg['staticSlot'];cm=load(pre/'manifest.json');sm=load(sta/'manifest.json');O=B/'evidence/PG24638-protocol-whole120-preflight-v1';assert not O.exists()
assert cm['actualExit']==0 and sm['inputHashes']==cm['inputHashes']
for n,h in cm['inputHashes'].items():assert sha(R/n)==h
assert set(cfg['testSources'])=={str(p.relative_to(R)) for p in (R/'src/schubert-nk-protocol/src/test/java').rglob('*.java')} and len(cfg['testSources'])==25
cases={};imports=[];sourceText={}
for n in cfg['testSources']:
 t=(R/n).read_text();sourceText[Path(n).stem]=t;names=re.findall(cfg['declarationRegex'],t);assert len(names)==t.count('@Test')
 if n in cfg['testClasses']:assert names;cases[cfg['testClasses'][n]]=names
 else:assert Path(n).name=='IndependentNamedFieldOracle.java' and not names
 for imp in re.findall(r'^import (?:static )?([^;]+);',t,re.M):
  assert imp.startswith(('dev.codex.schubert.nk.protocol.','java.','org.junit.'));imports.append(imp)
 for term in ['@Disabled','@ParameterizedTest','ProcessBuilder','Runtime.getRuntime','java.sql','jakarta.jms','java.net','Files.','@TempDir','Thread.sleep']:
  assert term not in t,(n,term)
assert len(cases)==24 and sum(map(len,cases.values()))==120
assert set(cfg['resources'])=={str(p.relative_to(R)) for p in (R/'src/schubert-nk-protocol/src/test/resources/protocol').glob('*.tsv')} and len(cfg['resources'])==5
for n in cfg['resources']:assert sha(R/n)==sha(pre/'resources'/n.split('/src/test/resources/')[1])
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert len(cfg['mainPaths'])==165 and all(sha(R/n)==nm['begin']['inputHashes'][n] for n in cfg['mainPaths'])
assert set(cm['dependencies'])=={nm['jars']['protocol']['path'],str(R.parent/'toolchain/m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar')}
for n,h in cm['dependencies'].items():assert sha(Path(n))==h
indexPath=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexPath)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';ix=load(indexPath)
with zipfile.ZipFile(nm['jars']['protocol']['path']) as z:
 allnames={n[:-6] for n in z.namelist() if n.endswith('.class')};assert allnames==set(cfg['targetPhysical'])==set(cfg['currentMainPhysical']) and len(allnames)==176
 for n in allnames:assert hashlib.sha256(z.read(n+'.class')).hexdigest()==ix[n]['sha256']==cfg['currentMainPhysical'][n]
 assert not any(held in n for n in z.namelist() for held in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
noCode=[n for n in allnames if not ix[n]['hasCode']];assert len(noCode)==13 and sum(n.endswith('package-info') for n in noCode)==7
for n in ['PayloadGoldenVectorTest','WebLogActionContractTest']:
 t=sourceText[n];assert 'finally {' in t and '.shutdownNow();' in t and 'awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS)' in t
# Closed-world per-finding applicability: host JUnit pools; local ordered maps; mandatory-null negatives.
items=sm['reports']['pmd']['items'];assert len(items)==17 and not sm['reports']['pmd']['processingErrors'] and not sm['reports']['checkstyle']['items'];review=[]
for item in items:
 owner=item['class'];method=item['method'];rule=item['rule'];line=int(item['beginline']);text=sourceText[owner].splitlines()[line-1]
 if rule=='DoNotUseThreads':
  assert owner in ['PayloadGoldenVectorTest','WebLogActionContractTest'];reason='Host-only JUnit pure-codec concurrency, nine sites; existing finally shutdownNow/await10 and finite get/latch, no J2EE container.'
 elif rule=='CloseResource':
  assert owner in ['PayloadGoldenVectorTest','WebLogActionContractTest'] and 'Executors.newFixedThreadPool' in text;reason='Explicit finally.shutdownNow plus successful awaitTermination10 assertion, including exceptional path; TWR unbounded close intentionally replaced.'
 elif rule=='UseConcurrentHashMap':
  assert owner=='IndependentNamedFieldOracle' and method in ['verifyAll','verifyType'] and item['variable'] in ['accessors','areas','reviewed','absent'];reason='Invocation-local maps: ordered accessors/absent and HashMap areas/reviewed grouping; synchronous reflection only, no shared pool state.'
 elif rule=='NullAssignment':
  assert (owner=='IndependentNamedFieldOracle' and method=='verifyType' and 'bad[n] = null' in text) or (owner=='WebLogActionContractTest' and method=='everyCanonicalConstructorReferenceRejectsNull' and 'invalid[i] = null' in text);reason='Intentional null constructor argument followed by assertThrows and typed cause verification; not a nullable production result.'
 else:raise AssertionError(item)
 review.append(dict(finding=item,lineTextSha256=hashlib.sha256(text.encode()).hexdigest(),applicable=False,reason=reason))
assert {r:sum(x['rule']==r for x in items) for r in {x['rule'] for x in items}}=={'DoNotUseThreads':9,'CloseResource':2,'UseConcurrentHashMap':4,'NullAssignment':2}
assert all(stage['actualExit']==0 for k,stage in sm['stages'].items() if k=='checkstyle') and sm['stages']['pmd']['actualExit']==4
changed='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/FieldCodecTest.java';assert subprocess.check_output(['git','diff','--name-only',cfg['beforeGitCommit'],'--','src/schubert-nk-protocol'],text=True).splitlines()==[changed]
raw=(R/changed).read_text();before=load(R/cfg['beforeMetadataPath']);original=subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+changed]);assert hashlib.sha256(original).hexdigest()==before['sha256'];a=raw.index('  @Test // PT-CODEC-EXC-001');z=raw.rfind('\n}');inverse=raw[:a-1]+raw[z+1:]
for line in ['import static org.junit.jupiter.api.Assertions.assertInstanceOf;\n','import static org.junit.jupiter.api.Assertions.assertNull;\n','import java.nio.charset.MalformedInputException;\n']:assert inverse.count(line)==1;inverse=inverse.replace(line,'',1)
assert inverse.encode()==original
oldcases={owner:re.findall(cfg['declarationRegex'],subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path],text=True)) for path,owner in cfg['testClasses'].items()};oldset={(c,n) for c,ns in oldcases.items() for n in ns};newset={(c,n) for c,ns in cases.items() for n in ns};assert len(oldset)==119 and oldset<=newset and newset-oldset=={('dev.codex.schubert.nk.protocol.codec.FieldCodecTest','malformedAndOverflowFailuresRetainDiagnosticCauseWithoutEchoingInput')}

# Exact current helper reflection targets remain Protocol semantics; no arbitrary external class loader.
helper=sourceText['IndependentNamedFieldOracle'];assert 'dev.codex.schubert.nk.protocol.layout.semantic.' in helper
assert all('SEMANTIC +' in line for line in helper.splitlines() if 'Class.forName(' in line)
# Exact finite path-contract counterexamples, no product execution.
for label,discovered in [('tests',{str(p.relative_to(R)) for p in (R/'src/schubert-nk-protocol/src/test/java').rglob('*.java')}),('resources',{str(p.relative_to(R)) for p in (R/'src/schubert-nk-protocol/src/test/resources/protocol').glob('*.tsv')})]:
 expected=set(cfg['testSources' if label=='tests' else 'resources']);assert expected==discovered
 assert expected!={str(R/p) for p in discovered} and expected!=set(sorted(discovered)[1:])
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=cm['inputHashes'],compileManifestSha256=sha(pre/'manifest.json'),staticManifestSha256=sha(sta/'manifest.json'),cases=cases,expectedTests=120,wholeFixtures=24,testSources=25,mainSources=165,physicalClasses=176,noCodeClasses=sorted(noCode),packageAnnotations=7,abstractInterfaces=6,resources={n:sha(R/n) for n in cfg['resources']},dependencies=cm['dependencies'],pmdRawFindings=17,pmdApplicability=review,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,original119MethodsPreserved=True,originalFieldSixRawRestored=True,newIndependentCauseMethods=1,pathNamespaceNegativeVectors=4,suppressionAdded=False,testFixtureExtraction=False,productTestsExecuted=0,heldFourPresentOnClasspath=False,backendOrRootVmNativeOperations=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,cases=120,wholeFixtures=24,physical=176,staticRaw=17,applicable=0,manifestSha256=sha(O/'manifest.json'))))
