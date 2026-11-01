"""Media display/links/stored pairs from synthetic DTOs only; no actual file/media/client/hash validation."""
import re
from pathlib import Path
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
ROOT=data.ROOT
PREFIX='dev/codex/schubert/nk/api/application/'
MAIN_UNITS={"dev/codex/schubert/nk/web/view/AnimationWatchViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/AnimationWatchViewModel","sha256":"45eb510139881b421370f9b05fd17cc688c832b9c2b71fb61e930e525075e648"},"dev/codex/schubert/nk/web/view/MusicTrackViewModel":{"module":"web","name":"dev/codex/schubert/nk/web/view/MusicTrackViewModel","sha256":"8bb4bc900c773b4e172c723827a8e558c83133fe882df9d11adf0237cecabf8e"}}
CLOSURES={"dev/codex/schubert/nk/web/view/AnimationWatchViewModel":["dev/codex/schubert/nk/web/view/AnimationWatchViewModel","dev/codex/schubert/nk/web/view/AnimationWatchViewModel$1"],"dev/codex/schubert/nk/web/view/MusicTrackViewModel":["dev/codex/schubert/nk/web/view/MusicTrackViewModel"]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'MediaDisplayContractTest':12}
PINS={'MediaDisplayContractTest':'1d746daa3a9f78797b5e2e12016d3ce7312310394132c4a4ddc032da8890baa5'}
TESTS={'MediaDisplayContractTest':ROOT/'tools/quality/architecture/MediaDisplayContractTest.java'}
PUBLIC_READS={"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java":"29af626632ac4c2727f9d0963c3967cb0be7eda57daf762a482268c467dc9232","src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/TopBarViewModel.java":"16afe37089d96cb31e7849e5bf5e289196588c6f4b8e1d4732fd402887e24a09","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/AuthenticationContext.java":"aaa18a4c954a425c943e8c30ea1752b665b249e86d8f1767e9e37f4aa61a6b66","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/UserRole.java":"b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java":"1f109d93cb6e8e802ab1a9c0484cfe48689253a34f1322111dfbce58bd0a8cde","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/media/VideoDescriptorResponseData.java":"7ed7ea562f6ee8a7fab5e299e4226c2a521c6014ddce4c5ea51d32986c71ae64","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/media/MusicTrackRecord.java":"c3e4d5a5e4de04642a361826684fa1f902681bbf455c754ad8fafb8c76ba262e","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/media/MusicTrackResponseData.java":"69270c63ce61efded7400fdea0494290e60d6e3e20927612a5ad4a676e984f81","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/PairRole.java":"b881ac09eba717b335039d9deb660ceaf1c7d40de7692ae583647f9efb94c454","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/VideoCategory.java":"e879c3cb991e034111d597f8d25bdf34c9796a54e242c74ce6da04e1203d54db","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/DisplayPath.java":"2718fe6494806fc87dc3d081f82ed220616a07d53bf6eb39a23de579b3c6e7e3","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/RelativePath.java":"0700ba6f2ef1263a690a0acd3030ad97455951c8dd66ebf632debeca6ff80fa1","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/Sha256Hex.java":"263a31fb0dc97901550336ceccc8d46ced8ecfd7cc78e8585f7ceb880bbebc4a","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/MediaMimeType.java":"a138a9d06104be25bf52c0401b34bea3230ae7670c65a1bcffd087469d6fd556","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/ContentDisposition.java":"1fa2440174428ce5529c8334891d36cfcc407fa12afeed607cf9077d4abbd629","src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/PathSyntax.java":"891c1c2ad213be265b4535abebdf8ee43a332ab952cabc4a9ca76372657b07b3"}
CURRENT_MUSIC_SOURCE=Path('/home/mini/codex/project1/schubert_project/program/app/src/main/java/dev/codex/schubert/service/MusicService.java')
CURRENT_MUSIC_SHA='92c750e05cb549db4be5d92e6d254bdf929aabc9fd88d81f261f3d62a74fb144'
EXTRAS={}
FIXTURES={}
SESSION='PG18230-MEDIA-DISPLAY12'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG18229-media-display-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    assert data.sha(CURRENT_MUSIC_SOURCE.read_bytes())==CURRENT_MUSIC_SHA
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG18218-current2925-user-display-registry-v1/manifest.json','d13f433b3f6d15e9bc44ac9fc88aeb0113b82847dbbd5d2781be47aef4baedb9')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&set(old['fullSourceUnits'])
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name] and relative=='tools/quality/architecture/MediaDisplayContractTest.java'
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        suite=next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name
        assert suite not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','getConnection(','System.getenv(','Runtime.getRuntime','addShutdownHook','removeShutdownHook','preserveFatal(','attachSecondary(','Executors.','new Thread','randomUUID','Instant.now','MessageDigest'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,independentNewQualityTests=12,selectedCompleteSuites=COUNTS,necessaryOriginalRepeats=0,pureMediaDisplayValuesOnly=True,syntheticDescriptorMetadataOnly=True,stubDescriptorContentHashNotVerified=True,actualFileContentOrHashValidated=False,storedMusicPairMetadataOnly=True,publicSyntheticAuthenticationContextValueOnly=True,syntheticAuthenticationContextValueUsed=True,nfcAndUtf8ValidationInvoked=True,memorySessionPrincipalValueOnly=True,currentIndependentOracleSourceReference=dict(path=str(CURRENT_MUSIC_SOURCE),sha256=CURRENT_MUSIC_SHA,readOnly=True,copiedToGit=False,executed=False),jdkNamedTimeZoneInitializationInvoked=False,maintenanceBusinessDateMethodInvoked=False,jdkTimezoneProviderCallsAndResourceReads=None,actualAdminMutationOrAuthorization=False,actualBusinessProviderInvoked=False,actualThrowableGraphTraversal=False,publicFixedUuidFixtureOnly=False,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualNetworkActions=0,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,platformJdkInitializationEffects=None,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg18230-media-display-twelve-pt-v1';run.OUT=data.BASE/'PG18230-media-display-twelve-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/MediaDisplayTwelveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MediaDisplayContractTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
