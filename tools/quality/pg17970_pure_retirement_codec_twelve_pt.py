"""Pure retirement codec4 plus necessary original canonical records8, no actual GC or native store."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
ROOT=data.ROOT
NAME='dev/codex/schubert/nk/batch/file/MaintenanceRecords'
VALUE='dev/codex/schubert/nk/batch/repository/MaintenanceRetirement'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='3c83d4b28a61325e4d997bfe7a92d92ea0f2ff79bbf03d4b8e37185c2335b80e'),VALUE:dict(module='batch',name=VALUE,sha256='8e9020955933dde695b79965d5cf61014b9a7ba919b96e88bf253a76357a42fb')}
CLOSURES={n:[n] for n in MAIN_UNITS}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'MaintenanceRecordsTest':8,'PureRetirementCodecContractTest':4}
PINS={'MaintenanceRecordsTest':'6a771cff5dad26f8b9f469667169f113b3e91be172fe52f400e53d543615dc32','PureRetirementCodecContractTest':'5cf213321f72aef288af4a65286a4d0e82561d3661144fa7413404abf9b1ef20'}
TESTS={'MaintenanceRecordsTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MaintenanceRecordsTest.java','PureRetirementCodecContractTest':ROOT/'tools/quality/architecture/PureRetirementCodecContractTest.java'}
PUBLIC_READS={'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRun.java':'c440d3e16da86b7814cf8fbd6247e48c1ab4cd6de2da3a114a38c308ae3c7ce4','src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MaintenanceActivation.java':'0467e9722cc3c46e238fcdb9e2d1deffde11b3a498e54e61c0f477d18440889e','src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MaintenanceCompletion.java':'3713fb2ce03a4ec926c4d193051373348da922c15d5f22e8f43cabd215b36dcd'}
EXTRAS={}
FIXTURES={}
SESSION='PG17970-PURE-RETIREMENT-CODEC-JOINT12'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17969-pure-retirement-codec-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17958-current2846-closed-projection-registry-v1/manifest.json','b65ad3a517cd4ef79b9587ec948e17bf397d873274d2f800861e1bcab59f2c94')
    assert old['source']==SOURCE and old['fullSourceUnits'][NAME]['four100'] is False and VALUE not in old['fullSourceUnits']
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]
        if name=='MaintenanceRecordsTest':assert current[relative]==PINS[name] and 'Path.of("target/maintenance-record-traces")' in text and 'Executors.newFixedThreadPool(8)' in text and 'future.get(5, TimeUnit.SECONDS)' in text
        else:assert relative=='tools/quality/architecture/PureRetirementCodecContractTest.java' and not any(x in text for x in ['Files.','Executors.','OwnedTransferDirectory','LinuxDirectoryCalls'])
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        suite=next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name
        assert (suite in old['suiteNames'])==(name=='MaintenanceRecordsTest')
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','getConnection(','System.getenv(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites={'MaintenanceRecordsTest':8},independentNewQualityTests=4,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=8,pureRetirementRecordCodecOnly=True,actualRetirementOrGcOperations=0,permissionIssuedOrPublished=False,declaredOwnTraceDirectory='target/maintenance-record-traces',originalPublicTraceFilesWritten=True,declaredOwnExecutorInstances=1,declaredMaximumPlatformWorkers=8,actualPlatformWorkers=None,declaredOwnTaskCount=64,perFutureTimeoutSeconds=5,declaredOwnedChildProcesses=0,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,cryptoOrKeyOperationsInvoked=False,publicFixedUuidFixtureOnly=True,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17970-pure-retirement-codec-twelve-pt-v1';run.OUT=data.BASE/'PG17970-pure-retirement-codec-twelve-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/PureRetirementTwelveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['PureRetirementCodecContractTest'];run.TEST_ROOT=TESTS['MaintenanceRecordsTest'].parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
