"""Whole original public proof correlation four; no launch, preflight or operational authority."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS=__import__('json').loads("{\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\",\"sha256\":\"0112b7877483404cc98f94750a1744c9af76a60b06e12696d6b7fd93b8300ea6\"},\"dev/codex/schubert/nk/batch/file/RootStartupPending\":{\"module\":\"batch\",\"name\":\"dev/codex/schubert/nk/batch/file/RootStartupPending\",\"sha256\":\"705fac625fca39f9c716ec82d84583676096bcf3c88fdb2ac490e8149d626fa8\"}}")
CLOSURES=__import__('json').loads("{\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\":[\"dev/codex/schubert/nk/batch/file/RootServiceLauncher\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$1\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Admission\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Measurement\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$NativeAdmission\"],\"dev/codex/schubert/nk/batch/file/RootStartupPending\":[\"dev/codex/schubert/nk/batch/file/RootStartupPending\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$1\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$LaunchRead\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$WaitIo\"]}")
METADATA=set(__import__('json').loads("[\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Admission\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$Measurement\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$NativeAdmission\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$LaunchRead\",\"dev/codex/schubert/nk/batch/file/RootStartupPending$WaitIo\",\"dev/codex/schubert/nk/batch/file/RootServiceLauncher$1\"]"))
GENERATED_METADATA={'dev/codex/schubert/nk/batch/file/RootServiceLauncher$1'}
EXTRAS=__import__('json').loads("{\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupLaunchFilesTest.java\":\"8a657af40f9d8a7fbb2b809ebbe2506e7790d874dee432d1fa92be7e1640960c\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupLaunchRecordTest.java\":\"cfb3ced853e96604d7746b195727258106aa75ec5af6d0f010dc7539f99f648d\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupPublicationFixture.java\":\"c0ce8671659feede55bb0d60dea3f1cc1bcb5d8fcce901aa52c22db7f21791e4\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java\":\"62a55866ed181dd886a8b5988fa5922675259b261ad31133a601c7b8361dcbf4\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/backup/BackupManifestFixture.java\":\"dc52d8ad7f4cc73b2947257e458bb8e36f10221789218812c44010c72951e976\"}")
COUNTS={'RootServiceProofTest':4}
PINS={'RootServiceProofTest':'3f128e8b94f7b2e7854525017a85e3ed2124089ea7c16637d84313b4204dcf8f'}
ROOT=data.ROOT
TESTS={'RootServiceProofTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceProofTest.java'}
FIXTURES={}
SESSION='PG16792-PUBLIC-ROOT-PROOF-ORIGINAL-FOUR'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16791-public-root-proof-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16785-current2385-public-permit-records-registry-v3/manifest.json','10ea750ad9969cf9180508cee21b5db01cd4690839b0f8d1084323231ef4fbd2')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.file.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','Files.','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','LinuxDirectoryCalls','RootStartupContext.create(','new StartupPermitFiles','getConnection(','new RootServiceLauncher(','new BackupPublicationFixture(','RootCurrentPermitPreflight.readNative(','RootStartupPending.observe('])
        assert 'RootServiceLauncher.proof(' in text and 'RootStartupPending.verifySelf(' in text
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    for path,pin in EXTRAS.items():assert current[path]==pin==data.sha((ROOT/path).read_bytes())
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,originalHelperSourceHashes=EXTRAS,reviewedInvokedHelperMethods=['StartupLaunchFilesTest.epoch','StartupLaunchRecordTest.bytes'],unselectedOriginalHelperTestsExecuted=False,publicCorrelationValuesOnly=True,generatedCompilerMetadata=sorted(GENERATED_METADATA),actualRootAuthorityOrLaunchInvoked=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16792-public-root-proof-original-four-pt-v1';run.OUT=data.BASE/'PG16792-public-root-proof-original-four-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/PublicRootProofFourCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RootServiceProofTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*[ROOT/p for p in EXTRAS]);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
