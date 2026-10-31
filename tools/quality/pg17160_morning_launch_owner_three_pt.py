"""Original whole ownership sequence3, no actual API/Web lifecycle or authority."""
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
NAME=PREFIX+'MorningStartupLaunchOwner'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='caca5ef9c6f8ab5e5084bf0ee363871b5e61fce4f023fd3daf9ca484faa0d99a')}
CLOSURES={NAME:[NAME+s for s in ['','$Stop','$Launch','$CompletionProgress','$CompletionRetirement','$Completion','$Started','$ApiRetained','$CompletionPhase']]}
METADATA={NAME+s for s in ['$Stop','$Launch','$CompletionRetirement','$Completion','$ApiRetained']}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningStartupLaunchOwnerTest':3}
PINS={'MorningStartupLaunchOwnerTest':'8c57963fbbed7665687dba4ec5cb7c249ccc6defa9afa7ff8d183ddaf3f1557a'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={}
FIXTURES={}
SESSION='PG17160-MORNING-LAUNCH-OWNER-ORIGINAL3'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17159-morning-launch-owner-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17142-current2606-root-scope-cleanup-value-registry-v1/manifest.json','3a25a5e1e3040a4638b0bd53833ec00915ae2b0393d71d7a0d17942060b2c56c')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    prior=data.read_checked(data.BASE/'PG16620-morning-pure-data-original-33-post-v1/manifest.json','a878d423f42737c284f3f7aa6cea59619e0da023340a532f5d3f24e93f3e2424')
    equivalent=data.read_checked(data.BASE/'PG16617-morning-static-review-equivalence-v1/manifest.json','b7589a46ea931fd4ad14e553453d8501eb8d5a790ececcfe31f74761bd124d15')
    assert prior['actualExit']==equivalent['actualExit']==0 and prior['source']==equivalent['source']==SOURCE
    assert prior['staticReviewEquivalenceSha256']=='b7589a46ea931fd4ad14e553453d8501eb8d5a790ececcfe31f74761bd124d15'
    assert set(prior['fullSourceUnits'][NAME]['physical'])==set(CLOSURES[NAME])
    assert equivalent['currentNormalManifestSha256']==COMPILE_SHA and equivalent['priorProductResultsTransferred'] is False
    verify(prior['invocation']);verify(equivalent['invocation'])
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='REUSED_SAME_SOURCE_FULL_REVIEW_FRESH_SEQUENCE_AND_WHOLE_TEST_REVIEW',priorSameSourceFullReviewSha256='a878d423f42737c284f3f7aa6cea59619e0da023340a532f5d3f24e93f3e2424',priorStaticEquivalenceSha256='b7589a46ea931fd4ad14e553453d8501eb8d5a790ececcfe31f74761bd124d15',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,syntheticLaunchStopSequenceCallbacksOnly=True,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17160-morning-launch-owner-three-pt-v1';run.OUT=data.BASE/'PG17160-morning-launch-owner-three-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/MorningLaunchOwnerThreeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningStartupLaunchOwnerTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()

