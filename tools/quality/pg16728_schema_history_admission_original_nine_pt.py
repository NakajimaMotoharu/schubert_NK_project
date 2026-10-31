"""Original whole nine hand-JDBC schema tests; explicit bootstrap module, no backend operations."""
import json
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
MAIN_UNITS=json.loads("{\"dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission\":{\"module\":\"bootstrap\",\"name\":\"dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission\",\"sha256\":\"4c0d9cd86b28b98d08d223dbb6f87c80f40d1b5226a9361add1ba28ea327fd2c\"},\"dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures\":{\"module\":\"bootstrap\",\"name\":\"dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures\",\"sha256\":\"bf179887c2496723d5ddb4ee0be02c5e599ecba781f5b8338367bb21648627a5\"}}")
CLOSURES=json.loads("{\"dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission\":[\"dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission\",\"dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission$Row\"],\"dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures\":[\"dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures\"]}")
METADATA=set()
COUNTS={'SchemaHistoryAdmissionTest':9}
PINS={'SchemaHistoryAdmissionTest':'c32a0e43d6d31a3478759a883c980099fdbb13ed97b9cf5985a0dfe24fe4e907'}
ROOT=data.ROOT
TESTS={'SchemaHistoryAdmissionTest':ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/SchemaHistoryAdmissionTest.java'}
EXTRAS={}
FIXTURES={}
SESSION='PG16728-SCHEMA-HISTORY-ADMISSION-ORIGINAL-NINE'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG16727-schema-history-fresh-review-binding-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG16718-current2361-supplementary-unit-registry-v1/manifest.json','ffe55277fc876f69ec79556013e41aaaf8cdb08acc61877281eb310636212c52')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.api.maintenance.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','DriverManager','ProcessBuilder','Files.','new BatchDatabaseFixture','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','Class.forName'])
        assert 'Proxy.newProxyInstance' in text and 'newVirtualThreadPerTaskExecutor' in text and 'CyclicBarrier(8)' in text
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['module']=='bootstrap' and row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    assert not any(v in (ROOT/path).read_text() for path in reviewed for v in ['TemporaryInfrastructureException','WebStartupException','DriverManager','ProcessBuilder','RootFailedStartRecovery'])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,module='bootstrap',namespaceIsNotModule=True,syntheticJdbcPortsOnly=True,actualJdbcBackendConnected=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16728-schema-history-admission-original-nine-pt-v1';run.OUT=data.BASE/'PG16728-schema-history-admission-original-nine-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/SchemaHistoryAdmissionNineCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['SchemaHistoryAdmissionTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
