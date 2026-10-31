"""Three complete original Root memory-fixture suites; no native provider or external resources."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/file/'
NAME=PREFIX+'MorningNewRunAdmission'
MAIN_UNITS={PREFIX+n:dict(module='batch',name=PREFIX+n,sha256=h) for n,h in [('MorningNewRunAdmission','7de62c1de31b281a763fba4de977756b63e466e288a220e6a494272194772b03'),('MorningResumeAdmission','999ccc9f609901804ddd967448a868875bc5f071df7e27cf66cd28a9daca1cd5')]}
CLOSURES={NAME:[NAME+s for s in ['','$2','$VerifiedContinuation','$Database','$2$1','$Originals','$1','$3','$FileWork','$OriginalProof','$DatabaseWork','$OriginalFiles','$Gate','$OwnedContinuation','$Files','$Continuation']],PREFIX+'MorningResumeAdmission':[PREFIX+'MorningResumeAdmission'+s for s in ['','$FileWork','$2$1','$2','$Files','$1','$Originals','$Database','$Gate','$DatabaseWork']]}
METADATA={NAME+s for s in ['$VerifiedContinuation','$Database','$Originals','$FileWork','$DatabaseWork','$Gate','$OwnedContinuation','$Files','$Continuation']}|{PREFIX+'MorningResumeAdmission'+s for s in ['$FileWork','$Originals','$Database','$Gate','$DatabaseWork']}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningOriginalCompletionTest':12,'UnsupportedOriginalProofTest':1}
PINS={'MorningOriginalCompletionTest':'60f7cf205cfc32988d42f2f01f026986aec011a74538be0c01bb1a3a945768d0','UnsupportedOriginalProofTest':'49acbf7c3702bb87f63b072ff227969cb03c8693a1de65cfc47a2c4c93f0442f'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={}
FIXTURES={}
SESSION='PG17120-ORIGINAL-COMPLETION-DEFAULT-ORIGINAL13'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17119-original-completion-default-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17110-current2586-stop-pass-postgres-rows-registry-v1/manifest.json','e734570cc128072dfbe6f9b28aa30452cea34dab787c7c530f2a2cc2d2c91fa6')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.file.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=True,syntheticCompletionPublicationCallbacksInvoked=True,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=4,declaredOwnExecutorInstances=3,declaredOwnTaskCount=3,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17120-original-completion-default-thirteen-pt-v1';run.OUT=data.BASE/'PG17120-original-completion-default-thirteen-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/OriginalCompletionDefaultThirteenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningOriginalCompletionTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
