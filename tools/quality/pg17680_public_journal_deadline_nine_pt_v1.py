"""Whole original public journal7 plus borrowed deadline2; own JVM provider registry restored."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/'
NAME=PREFIX+'platform/BrokerJournalEvidence'
CLIENT=PREFIX+'mq/ArtemisManagementReadinessClient'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='18f067e88b43658b276d06a0ef889adde32d039a50e2b1ba8dd654488d2d70bb'),CLIENT:dict(module='batch',name=CLIENT,sha256='3eb82d01455cf8d2932baf0bc9ed57c2d843a5bd7e071cdc285958a370413f73')}
CLOSURES={NAME:[NAME,NAME+'$Anchor',NAME+'$Summary'],CLIENT:[CLIENT,CLIENT+'$Reader',CLIENT+'$OperationEncoder',CLIENT+'$OwnedOperation',CLIENT+'$MessageWriter',CLIENT+'$Exchange']}
METADATA={n for n in CLOSURES[CLIENT] if n!=CLIENT}
METADATA_FLAGS={n:1537 if n.endswith('$OwnedOperation') else 1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'BrokerJournalEvidenceTest':7,'ArtemisParentDeadlineTest':2}
PINS={'BrokerJournalEvidenceTest':'73ec7a8bca1a6540dec83520b7072b56fd7c988e55d9d1a86afb67b0a9125a02','ArtemisParentDeadlineTest':'824d9ebd325286b76120488d7ef6a54d941a94eeb8939b493c5575d2d0d5eaad'}
ROOT=data.ROOT
TESTS={'BrokerJournalEvidenceTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/BrokerJournalEvidenceTest.java','ArtemisParentDeadlineTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisParentDeadlineTest.java'}
PUBLIC_READS={}
EXTRAS={}
FIXTURES={}
SESSION='PG17680-PUBLIC-JOURNAL-DEADLINE-ORIGINAL9'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17680-public-journal-deadline-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17668-current2784-root-entry-denial-registry-v1/manifest.json','b0335a61ca2f6486983b8968b662200f4df8326e6494c17ab448c412012ab375')
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
    test=TESTS['BrokerJournalEvidenceTest'].read_text()
    assert 'Security.removeProvider(provider.getName())' in test and 'Security.insertProviderAt(original[i], i + 1)' in test and 'assertArrayEquals(original, Security.getProviders())' in test and 'finally {' in test
    deadline=TESTS['ArtemisParentDeadlineTest'].read_text()
    assert 'thread.start();' in deadline and 'thread.join();' in deadline and 'ArtemisManagementReadinessClient.withParentDeadline(' in deadline
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=True,cryptoOrKeyOperationsInvoked=True,testOwnJcaProviderRegistryTemporarilyModifiedAndFinallyRestored=True,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,syntheticPermitRecordConstructionOnly=False,nativeNamedReadNullGuardOnlyInvoked=False,actualPermitNamespaceLookups=0,actualRootOsAdmissionInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=1,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17680-public-journal-deadline-nine-pt-v1';run.OUT=data.BASE/'PG17680-public-journal-deadline-nine-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/PublicJournalDeadlineNineCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['BrokerJournalEvidenceTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={'ArtemisParentDeadlineTest':TESTS['ArtemisParentDeadlineTest']}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
