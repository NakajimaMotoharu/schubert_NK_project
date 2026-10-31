"""Original whole no-prior Broker eight; only reviewed injected memory ports and two public golden resources."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/platform/'
NAME='dev/codex/schubert/nk/batch/file/MorningGateEvidence'
MAIN_UNITS={n:dict(module='batch',name=n,sha256=h) for n,h in [(NAME,'c5c0295c1c8da89bad0890cad123366462e46941e6902f987dc17b77bc515d8a'),(PREFIX+'MorningUnitTerminals','d1252e2babbd2d46e807d449f9d98020602b5d83b63ab6ba533a63a61df695d8'),(PREFIX+'BrokerJournalEvidence','18f067e88b43658b276d06a0ef889adde32d039a50e2b1ba8dd654488d2d70bb')]}
CLOSURES={NAME:[NAME],PREFIX+'MorningUnitTerminals':[PREFIX+'MorningUnitTerminals'+s for s in ['','$Observation','$DetailedObservation','$Snapshot']],PREFIX+'BrokerJournalEvidence':[PREFIX+'BrokerJournalEvidence'+s for s in ['','$Anchor','$Summary']]}
METADATA={PREFIX+'MorningUnitTerminals'+s for s in ['$Observation','$DetailedObservation']}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningGateEvidenceTest':5,'MorningGateEvidenceBrokerTest':3,'MorningStopEvidenceTest':3,'MorningUnitTerminalsTest':6}
PINS={'MorningGateEvidenceTest':'d5fd953cc959484c7154a354330689a2d6036796f135a2a2e2dd3db6aa09828d','MorningGateEvidenceBrokerTest':'fba18d65fbd38f4155fccfd3105cb3f06b89915c606a8999e478762c7a2e80b0','MorningStopEvidenceTest':'28f1bfc36608177e1dfce5f7664ae5df1d97a32f26eac3d7ec85ae3c79049351','MorningUnitTerminalsTest':'d9944155c252153f0ac407a688f2d9b79f2dc34571a63662f42b4be06f14892d'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'+('file/' if n.startswith('MorningGate') else 'platform/')+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java':h for n,h in {"MorningPreviousBrokerTest":"893dab081db5bbb10fd45d70329df92f29496f885dfa86a69661f3aa7b970823","BrokerJournalEvidenceTest":"73ec7a8bca1a6540dec83520b7072b56fd7c988e55d9d1a86afb67b0a9125a02","MorningBrokerUnitCycleTest":"298e637df1d718f5a04aff184bdc26cc21b9038b314b318e2fda8658d5eb3eb0","RootStartupContextTest":"f3de04b3c6043aed5e6871bc1de15b8108da8cf7adacad206d0a8a0b88a71811","MaintenanceUnitTerminationTest":"458e93febbe7700c7f84034573a2464fcbb52edc929fe6826cfdc72c618d0ced","BackupUnitTerminationTest":"077c29d1aad07c974ba31aa621278a0c8589359363b3f9ea526e0efc3b4702ea","InspectorUnitProbeFixture":"75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b","InspectorUnitSnapshotTest":"edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63"}.items()}
FIXTURES={'src/schubert-nk-batch/src/test/resources/ops/'+n:h for n,h in {"issuer-stop-journal.jsonl":"30cc188d896c73c44b5b4a9b508f0eef46d7cc9cbd3043a7ccd32781899d533d","issuer-stop-journal-content-golden.txt":"e3a86812641c1394772a2e492a72624fb2c504b8b033358558e8ee6d79a74a5e","issuer-stop-present-native-golden.txt":"5accf336b01e47f2066f81e88f11fa1ed50da16459ec40589bf278003d8ec4e4","issuer-stop-present-boot-golden.txt":"3ac3515bff38e3000b3f5833d5d95d2cffa917b7e900656ca5d5118e848bb15b","issuer-stop-absent-native-golden.txt":"cd1b893d5a26f952e6fd0b2a6d4bf59107ef93ed1661f80e5aac1f6d623d1567","issuer-stop-absent-boot-golden.txt":"2d56c8c95000e66a5917fad6b643e866ac97549704fbfca9b79a290943e030cf","issuer-broker-input.json":"6dfd7d71d4a20d6b39e792c37f21e7b0fdb5500a4a3f1d55885995afcb9fe910","issuer-broker-golden.txt":"0d2dde48a389a02ab67232d2d7a7b1cb292840ffab589784523a4836a0c9491d"}.items()}
SESSION='PG17070-MORNING-GATE-EVIDENCE-ORIGINAL17'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17069-morning-gate-evidence-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17060-current2547-no-prior-broker-registry-v1/manifest.json','ef523fa81539f44dd15dcf0ac3df1f50acce34183615ad21ed9514e15f534a87')
    assert old['source']==SOURCE and set(MAIN_UNITS)-old['fullSourceUnits'].keys()=={NAME,PREFIX+'MorningUnitTerminals'}
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert relative.split('/src/test/java/',1)[1][:-5].replace('/','.') not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in {**EXTRAS,**FIXTURES}.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=True,memoryJournalQueryPortsOnly=True,publicDigestOnly=True,cryptoOrKeyOperationsInvoked=True,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,actualRootMemoryFixtureOnly=True,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,declaredOwnThreadCount=0,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=True,publicRandomUuidValueOnly=True,testPublicGoldenResourcesRead=True,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17070-morning-gate-evidence-seventeen-pt-v1';run.OUT=data.BASE/'PG17070-morning-gate-evidence-seventeen-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/MorningGateEvidenceSeventeenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningStopEvidenceTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n.startswith('MorningGate')}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
