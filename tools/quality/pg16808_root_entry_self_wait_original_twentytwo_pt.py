"""Coherent original Root entry/self/wait/public-boundary22; no native authority or real startup."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS=__import__('json').loads("{\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\",\"sha256\":\"0112b7877483404cc98f94750a1744c9af76a60b06e12696d6b7fd93b8300ea6\"},\"dev/codex/schubert/nk/batch/file/RootStartupPending\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/RootStartupPending\",\"sha256\":\"705fac625fca39f9c716ec82d84583676096bcf3c88fdb2ac490e8149d626fa8\"},\"dev/codex/schubert/nk/batch/file/StartupLaunchRecord\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/StartupLaunchRecord\",\"sha256\":\"2d5590794349337b7351f97582511f4c2244b8ae3fe42a7976202eb766cf05d5\"}}")
CLOSURES=__import__('json').loads("{\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\":[\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$1\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Admission\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Measurement\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$NativeAdmission\"],\"dev/codex/schubert/nk/batch/file/RootStartupPending\":[\"dev/codex/schubert/nk/batch/file/RootStartupPending\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$1\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$LaunchRead\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$WaitIo\"],\"dev/codex/schubert/nk/batch/file/StartupLaunchRecord\":[\"dev/codex/schubert/nk/batch/file/StartupLaunchRecord\",\"dev/codex/schubert/nk/batch/file/StartupLaunchRecord$DigestFactory\"]}")
METADATA=set(__import__('json').loads("[\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Admission\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Measurement\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$NativeAdmission\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$LaunchRead\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$WaitIo\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$1\",\"dev/codex/schubert/nk/batch/file/StartupLaunchRecord$DigestFactory\"]"))
GENERATED_METADATA={'dev/codex/schubert/nk/batch/file/RootServiceLauncher$1'}
EXTRAS=__import__('json').loads("{\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupLaunchRecordTest.java\":\"cfb3ced853e96604d7746b195727258106aa75ec5af6d0f010dc7539f99f648d\"}")
TEST_PROFILE=__import__('json').loads("{\"RootServiceLauncherTest\":{\"count\":6,\"path\":\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceLauncherTest.java\",\"sha256\":\"14d8bb0e16eaf77fde9fe21d3b430910c1543b6342cee297ba139f5effd54493\"},\"RootStartupPendingTest\":{\"count\":3,\"path\":\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootStartupPendingTest.java\",\"sha256\":\"71d26b092b5e748ba04d016255166df48217d011bf9bf934d5ed1103e8d23450\"},\"RootPendingWaitTest\":{\"count\":12,\"path\":\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootPendingWaitTest.java\",\"sha256\":\"7b139fee9969ef34f1cba729f428c8160d1700e73a660dfb0d4bd512f7f47936\"},\"StartupLaunchBoundaryTest\":{\"count\":1,\"path\":\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupLaunchBoundaryTest.java\",\"sha256\":\"3f75a1fd93c104826017bd7932ef6d021127fe3b5d23663c93b0934e8a47fba7\"}}")
ROOT=data.ROOT
TESTS={n:ROOT/row['path'] for n,row in TEST_PROFILE.items()}
COUNTS={n:row['count'] for n,row in TEST_PROFILE.items()}
PINS={n:row['sha256'] for n,row in TEST_PROFILE.items()}
FIXTURES={}
SESSION='PG16808-ROOT-ENTRY-SELF-WAIT-ORIGINAL-TWENTYTWO'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16807-root-entry-self-wait-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16798-current2389-public-root-proof-registry-v1/manifest.json','5da5ac0e0be0e876a9a80844a8e765fb36be1b3733d4de0968cc99ef3d96640d')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    file_call=lambda value:re.search(r'(?<![A-Za-z0-9_$])Files\s*\.',value) is not None
    lexical=[('Files.readString(path)',True),('java.nio.file.Files.readString(path)',True),('ServiceConfigFiles.Service.values()',False),('StartupLaunchFilesTest.epoch()',False)]
    assert all(file_call(value) is expected for value,expected in lexical)
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.file.'+name not in old['suiteNames']
        assert not file_call(text) and not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','java.nio.file.','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','LinuxDirectoryCalls','RootStartupContext.create(','new StartupPermitFiles','getConnection(','new RootServiceLauncher(','.setAccessible(','.newInstance(','RootStartupPending.observe('])
    text=TESTS['RootServiceLauncherTest'].read_text()
    assert text.count('.getDeclaredConstructor()')==1 and '.getMethod("main", String[].class)' in text
    assert 'Thread.interrupted()' in TESTS['RootPendingWaitTest'].read_text()
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    for path,pin in EXTRAS.items():assert current[path]==pin==data.sha((ROOT/path).read_bytes())
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,originalHelperSourceHashes=EXTRAS,reviewedInvokedHelperMethods=[],unselectedOriginalHelperTestsExecuted=False,publicCorrelationValuesOnly=True,metadataReflectionOnly=True,ownThreadInterruptRestoredByTest=True,generatedCompilerMetadata=sorted(GENERATED_METADATA),actualRootAuthorityOrLaunchInvoked=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16808-root-entry-self-wait-original-twentytwo-pt-v1';run.OUT=data.BASE/'PG16808-root-entry-self-wait-original-twentytwo-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/RootEntrySelfWaitTwentyTwoCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RootServiceLauncherTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='RootServiceLauncherTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,*[ROOT/p for p in EXTRAS]);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
