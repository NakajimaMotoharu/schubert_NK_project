"""Whole four classes; fixed source inverses, independent old literals, typed closure and static applicability."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import re
import subprocess
import zipfile
import class_reference_metadata as metadata

R=Path.cwd();B=R/'evidence/01_PT/005_NK-MSG-001';C=B/'input/038_jms_memory_bounded_scope.json';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(C);RUNS=R.parent/'pgpt-runs/PG379';O=R/cfg['preflightManifest'];assert not O.parent.exists()
pre=load(RUNS/cfg['compileSlot']/'manifest.json');sta=load(RUNS/cfg['staticSlot']/'manifest.json');assert pre['actualExit']==0 and pre['inputHashes']==sta['inputHashes']
for name,h in pre['inputHashes'].items():assert sha(R/name)==h
# Fixed snippet comparison only, not a general Java parser; strings retain their whitespace.
def tokens(text):
    assert '"""' not in text
    return ''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',text))


def inverse(filename,text):
    out=tokens(text)
    if filename=='JmsRequestReplyClientTest.java':
        needle='assertTrue(latch.await(5,TimeUnit.SECONDS));';assert out.count(needle)==1
        return out.replace(needle,'latch.await();',1)
    maps=({'firstCompletion':('pending',1),'secondCompletion':('pending',1),'completion':('pending',2)} if filename=='ReplyCorrelationRegistryTest.java' else {'completion':('pending',1),'firstCompletion':('timely',1),'secondCompletion':('timely',1),'lateCompletion':('late',1),'finalCompletion':('pending',1)})
    for name,(receiver,count) in maps.items():
        expression=receiver+'.completion().toCompletableFuture()'
        declaration='var'+name+'='+expression+';assertTrue('+name+'.isDone());'
        assert out.count(declaration)==count,(filename,name,'declaration')
        calls=(0,1) if name=='lateCompletion' else ((1,1) if name=='completion' else (1,0))
        assert (out.count(name+'.join()'),out.count(name+'::join'))==calls,(filename,name,'exact captured view call')
        out=out.replace(declaration,'')
        out=out.replace(name+'::join','()->'+expression+'.join()')
        out=out.replace(name+'.join()',expression+'.join()')
    if filename=='ReplyCorrelationTerminalRaceTest.java':
        assert out.count('assertTrue(independent.isDone());')==1
        out=out.replace('assertTrue(independent.isDone());','',1)
    return out


inverses=[];join_sites=0;guard_count=0;new_sources={}
for name in cfg['changedTestSources']:
    path=next(Path(n) for n in cfg['testClasses'] if Path(n).name==name);old=(R/cfg['beforeDirectory']/name).read_text();new=(R/path).read_text();assert inverse(name,new)==tokens(old)
    joins=old.count('.join()');guards=(new.count('.isDone()')-old.count('.isDone()'))
    join_sites+=joins;guard_count+=guards;new_sources[name]=new
    inverses.append(dict(path=str(path),beforeSha256=sha(R/cfg['beforeDirectory']/name),afterSha256=sha(R/path),allOriginalTokensAndOracleLiteralsPreserved=True,terminalJoinSites=joins,completionGuardsAdded=guards))
assert join_sites==11 and guard_count==10
# Remove/forge completion guards, state-mutating timeout, alias view, and oracle changes all fail inversion.
negatives=[]
for name,old,new in [('JmsRequestReplyClientTest.java','assertTrue(latch.await(5, TimeUnit.SECONDS));','latch.await();'),('ReplyCorrelationRegistryTest.java','assertTrue(firstCompletion.isDone());','assertTrue(true);'),('ReplyCorrelationRegistryTest.java','firstCompletion.join()','pending.completion().toCompletableFuture().join()'),('ReplyCorrelationTerminalRaceTest.java','assertTrue(independent.isDone());',''),('ReplyCorrelationTerminalRaceTest.java','lateCompletion::join','lateCompletion.orTimeout(5, TimeUnit.SECONDS)::join'),('ReplyCorrelationTerminalRaceTest.java','new byte[] {7, 8, 9}','new byte[] {7, 8, 0}')]:
    text=new_sources[name];assert old in text;mutated=text.replace(old,new,1);expected=tokens((R/cfg['beforeDirectory']/name).read_text())
    try:valid=inverse(name,mutated)==expected
    except AssertionError:valid=False
    assert not valid
    negatives.append(dict(source=name,mutation=old))
cleanup=next(n for n in cfg['testClasses'] if n.endswith('/JmsRequestReplyCleanupTest.java'));assert hashlib.sha256(subprocess.check_output(['git','show',cfg['baselineHead']+':'+cleanup])).hexdigest()==sha(R/cleanup)
expected=set()
for path,cls in cfg['testClasses'].items():
    text=(R/path).read_text();expected.update((cls,n) for n in re.findall(r'@Test\s+void\s+(\w+)\s*\(',text))
    assert not any(word in text for word in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','Class.forName','ServiceLoader','setAccessible','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
assert len(expected)==21
assert not sta['reports']['checkstyle']['items'] and not sta['reports']['checkstyle']['processingErrors'] and not sta['reports']['pmd']['processingErrors']
items=sta['reports']['pmd']['items'];sites={('JmsRequestReplyClientTest',n) for n in [132,133,142,169,174,294]}|{('ReplyCorrelationRegistryTest',n) for n in [111,115]}|{('ReplyCorrelationTerminalRaceTest',n) for n in [36,44,50,56,96,101]}
assert len(items)==14 and {(r['class'],int(r['beginline'])) for r in items}==sites and all(r['rule']=='DoNotUseThreads' for r in items)
assert sta['stages']['pmd']['actualExit']==4 and sta['stages']['checkstyle']['actualExit']==0
classifications=[]
for row in items:
    reason={'interruptedWaitRemovesRegistrationAndRestoresInterruptFlag':'Own waiting thread; sent.await2, interrupt/join2 with finally repeated interrupt/join; original interrupt-flag restoration oracle unchanged.', 'approvedConfiguredWaitsAccept1To20AndRejectTheNextWithoutSending':'Own 1/12/20 executor tasks; entered2 and results2 seconds, sender latch newly5SECONDS/assert and finally countDown before TWR; capacity literal oracle unchanged.', 'await':'InterruptedException catch restores own caller flag and wraps same synthetic JMS failure; new CountDownLatch await5 is asserted, never a normal pass on timeout.', 'oneOfOneHundredSimultaneousResponsesWins':'Own100 tasks/16threads; start5/results5, owned TWR. Exact captured completion now isDone before original join; winner/late/clone oracle unchanged.', 'terminalRaceHasOneWinnerAndReturnsThePermit':'Own3 tasks with finally release/start5 and exact terminal get10; same captured completion isDone before original success/exception join. No injected timeout or exception-type replacement.', 'concurrentRegistrationsRespectCapacityAndReuseAllSlots':'Own20 registration tasks; release finally/start5/get10/TWR, original2accepted18rejected/full capacity reuse preserved.'}[row['method']]
    classifications.append(dict(finding=row,applicableViolation=False,reason='JUnit-only ownership test outside J2EE runtime. '+reason))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for name in cfg['mainPaths']:assert sha(R/name)==nm['begin']['inputHashes'][name]
for module in cfg['modules']:assert sha(Path(nm['jars'][module]['path']))==nm['jars'][module]['sha256']
for name,h in pre['dependencies'].items():assert sha(Path(name))==h
sdk=[]
for name,h in cfg['sdkDependencies'].items():
    p=Path(name);assert sha(p)==h
    with zipfile.ZipFile(p) as z:
        names=set(z.namelist());assert not names.intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin'})
        mf=z.read('META-INF/MANIFEST.MF').decode() if 'META-INF/MANIFEST.MF' in names else '';assert not re.search(r'^Class-Path:',mf,re.M)
    sdk.append(dict(path=name,sha256=h,jdbcDriverDescriptor=False,compilerPluginDescriptor=False,manifestClasspath=False))
index_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(index_path)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(index_path)
physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert physical==cfg['currentMainPhysical'] and len(physical)==5
plan_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12918-coordinator-corrected-plan-v1/manifest.json';assert sha(plan_path)=='3491b6d92468eee54d6aba15e1efe500fa82676ac5bdc4bdfdcf53fbe58953c3';plan=load(plan_path);paths=set(plan['eligibilityClosureSourceHashes']);assert len(paths)==6
assert all(sha(R/n)==h for n,h in plan['eligibilityClosureSourceHashes'].items())
constant_path=B/'evidence/PG24237-jms-constant-reference-javap-v1/manifest.json'
constant=load(constant_path)
assert constant['actualExit']==0 and constant['normalWebJarSha256']==nm['jars']['web']['sha256']
assert constant['headerLengthInstruction']==256 and constant['constantOwnerInstructionsAbsent'] is True
assert sha(constant_path.parent/'metadata.stdout')==constant['metadataSha256']
assert 'LayoutDefinition' not in (constant_path.parent/'metadata.stdout').read_text()
graph=[]
for name,row in index.items():
    if row['path'] not in paths:continue
    assert not any(s in name for s in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
    module='web' if '/schubert-nk-web/' in row['path'] else 'protocol'
    with zipfile.ZipFile(nm['jars'][module]['path']) as z:raw=z.read(name+'.class')
    assert hashlib.sha256(raw).hexdigest()==row['sha256'];info=metadata.read(raw);refs=[v for v in info['references'] if v.startswith('dev/codex/schubert/nk/') and not v.endswith('/package-info')]
    constant_only=[v for v in refs if name=='dev/codex/schubert/nk/web/messaging/JmsRequestReplyClient' and v==constant['compileTimeConstantOwner']]
    assert all(v in index and index[v]['path'] in paths for v in refs if v not in constant_only)
    graph.append(dict(className=name,source=row['path'],sourceSha256=sha(R/row['path']),productReferences=refs,nonRuntimeCompileTimeConstantOwners=constant_only))
assert {r['source'] for r in graph}==paths
O.parent.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=pre['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),originalCurrentMainCodeByteSetComplete=True,physical=physical,expectedTests=21,changedTestSources=3,changedLatchSites=1,terminalJoinSites=11,exactViewCompletionGuards=10,sourceInverses=inverses,sourceInverseNegativeChecks=negatives,allOriginalTestOtherTokensAndOraclesPreserved=True,noTimeoutPromiseMutation=True,noNewFixtureOrMethodExtraction=True,staticClassifications=classifications,pmdRawFindings=14,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,suppressionAdded=False,sdkReview=sdk,originalEligibilitySourcesSame=6,sourceGraph=graph,normalPositiveMainIndex={'path':str(index_path.relative_to(R)),'sha256':sha(index_path)},currentProductionMain=nm['source'],originalWholeTestClassSelection=True,actualBackendOperationsAuthorized=False,heldFourRuntimeOperationsAuthorized=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,tool={'path':str(Path(__file__)),'sha256':sha(Path(__file__))})
O.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedTests=21,targetPhysical=5,graphPhysical=len(graph),pmdRaw=14,applicable=0,sourceInverseNegatives=6,manifestSha256=sha(O))))
