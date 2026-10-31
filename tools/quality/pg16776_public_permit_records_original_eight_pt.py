"""Whole original public-value record tests; SHA256 over golden data, never real startup authority."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/batch/file/StartupPermitRecords'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='9cefa5e6b31443b0de40c493e47776f4905cbff928a75597d1404913a36c079f')}
CLOSURES={NAME:[NAME,NAME+'$State',NAME+'$Permit',NAME+'$Epoch',NAME+'$DigestFactory']}
METADATA={NAME+'$DigestFactory'}
COUNTS={'StartupPermitRecordsTest':8}
PINS={'StartupPermitRecordsTest':'119fe6e726f08d5a71ce0aaf64939a665b64a280d9b0a1f8be03a3b52bd9c633'}
ROOT=data.ROOT
TESTS={'StartupPermitRecordsTest':ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StartupPermitRecordsTest.java'}
EXTRAS={}
FIXTURES={}
SESSION='PG16776-PUBLIC-PERMIT-RECORDS-ORIGINAL-EIGHT'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16775-public-permit-records-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16766-current2377-bootstrap-closing-registry-v1/manifest.json','766715c00a12e9a98cb962318b0cade732abfd457a5a2f800e35b1b41b2672ae')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.file.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','Files.','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName','LinuxDirectoryCalls','RootStartupContext','new StartupPermitFiles','getConnection('])
        assert 'MessageDigest.getInstance("SHA-256").digest(bytes(GOLD))' in text and 'Executors.newFixedThreadPool(4)' in text and 'i < 32' in text
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    for helper in ['BatchRun','MaintenanceActivation']:
        path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/'+helper+'.java'
        assert current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=current[path]
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,publicRecordValuesOnly=True,publicDigestOnly=True,actualPermitIssueSignPublishOrRetire=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16776-public-permit-records-original-eight-pt-v1';run.OUT=data.BASE/'PG16776-public-permit-records-original-eight-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/PublicPermitRecordsEightCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['StartupPermitRecordsTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
