"""Whole original Root entry denials and fake descriptor ownership; no real Root/native operation."""
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
NAME=PREFIX+'RootServiceExecutableAdmission'
PENDING=PREFIX+'RootStartupPending'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='04efbba4deb8101b038a9faa978c090fc3227e86dc4658abc4b5dfde959d28c7'),PENDING:dict(module='batch',name=PENDING,sha256='705fac625fca39f9c716ec82d84583676096bcf3c88fdb2ac490e8149d626fa8')}
CLOSURES={NAME:[NAME,NAME+'$RootDescriptor',NAME+'$Capability',NAME+'$Work',NAME+'$DigestFactory'],PENDING:[PENDING,PENDING+'$1',PENDING+'$WaitIo',PENDING+'$LaunchRead']}
METADATA={NAME+'$Capability',NAME+'$Work',NAME+'$DigestFactory',PENDING+'$WaitIo',PENDING+'$LaunchRead'}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'RootEntryRejectionTest':4}
PINS={'RootEntryRejectionTest':'c357c994da60f5b4b1a544a7dd0625855f1304a7c732c861e04f1ad30ce0bc4c'}
ROOT=data.ROOT
TESTS={'RootEntryRejectionTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootEntryRejectionTest.java'}
PUBLIC_READS={}
EXTRAS={"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java":"62a55866ed181dd886a8b5988fa5922675259b261ad31133a601c7b8361dcbf4","src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupManifestFixture.java":"dc52d8ad7f4cc73b2947257e458bb8e36f10221789218812c44010c72951e976","src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceProofTest.java":"3f128e8b94f7b2e7854525017a85e3ed2124089ea7c16637d84313b4204dcf8f","src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceExecutableAdmissionTest.java":"0eb588b1c26c5f43be596c2f7c33548eaca39981c6a95bea4c602cfd0084681f","src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupLaunchRecordTest.java":"cfb3ced853e96604d7746b195727258106aa75ec5af6d0f010dc7539f99f648d","src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupLaunchFilesTest.java":"8a657af40f9d8a7fbb2b809ebbe2506e7790d874dee432d1fa92be7e1640960c","src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupPublicationFixture.java":"c0ce8671659feede55bb0d60dea3f1cc1bcb5d8fcce901aa52c22db7f21791e4","src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/RootContextNoIoFixture.java":"1e5dff06d744554b88cb4d46fd342d8da7dcd99380516c9acb984db19921ae84"}
FIXTURES={}
SESSION='PG17661-ROOT-ENTRY-DENIAL-ORIGINAL4-V2'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17661-root-entry-denial-review-v2'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17648-current2780-permit-data-registry-v1/manifest.json','ffd247fe95c7560885b25d0eff356d673841c8d0959e153ba9dc35c7d3c0560a')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    test=TESTS['RootEntryRejectionTest'].read_text()
    assert 'new RootContextNoIoFixture()' in test and 'assertEquals(0, fixture.calls())' in test
    assert 'int value = 319;' in test and 'assertEquals(319, actual)' in test
    context=ROOT/'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/RootStartupContext.java'
    assert data.sha(context.read_bytes())==current[str(context.relative_to(ROOT))]
    fixture=(ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/RootContextNoIoFixture.java').read_text()
    assert 'new RootStartupContext.Io()' in fixture and 'throw denied();' in fixture and 'new RootStartupContext.NativeIo' not in fixture
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,syntheticPermitRecordConstructionOnly=True,nativeNamedReadNullGuardOnlyInvoked=True,rootContextInjectedAllDenyConstructorOnly=True,declaredFakeDescriptor319Only=True,actualPermitNamespaceLookups=0,actualRootOsAdmissionInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17661-root-entry-denial-four-pt-v2';run.OUT=data.BASE/'PG17661-root-entry-denial-four-pt-v2'
    run.HELPER=ROOT/'tools/quality/architecture/RootEntryDenialFourCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RootEntryRejectionTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
