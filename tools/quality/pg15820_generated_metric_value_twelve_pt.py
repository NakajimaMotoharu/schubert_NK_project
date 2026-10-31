"""Whole original generated metric value12; nested values only, prior whole Source proofs preserved."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/'
MAINS={"api/monitoring/DbPoolMetricRecorder":"11a8f25926ef4727e019349b1965b97c456eb46f5f82d2697506610f12e4241c","api/monitoring/OutboxRowsMetricRecorder":"c0d709475517e31192afe8486be24f7a88232a87dd43d0db4e77ce34dd78a7d5","api/monitoring/AsyncJobMetricRecorder":"bcbe814f37ba7a9cdba482369fa7ab70c5688713249ab780c35b6eeba3190cd6","api/monitoring/OperationMismatchMetricRecorder":"74cef118229b3163b561702d8001e9cd0509bcc6ff6d6a56d2ccccf98de9de55","web/monitoring/HttpMetricContract":"019f126d38fdfbfd60baf8f38c254201db2427e7a0c2087e052712812a889c03"}
CLOSURES={"api/monitoring/DbPoolMetricRecorder":["api/monitoring/DbPoolMetricRecorder","api/monitoring/DbPoolMetricRecorder$Counts","api/monitoring/DbPoolMetricRecorder$State"],"api/monitoring/OutboxRowsMetricRecorder":["api/monitoring/OutboxRowsMetricRecorder","api/monitoring/OutboxRowsMetricRecorder$Counts","api/monitoring/OutboxRowsMetricRecorder$Status"],"api/monitoring/AsyncJobMetricRecorder":["api/monitoring/AsyncJobMetricRecorder","api/monitoring/AsyncJobMetricRecorder$Snapshot","api/monitoring/AsyncJobMetricRecorder$State"],"api/monitoring/OperationMismatchMetricRecorder":["api/monitoring/OperationMismatchMetricRecorder","api/monitoring/OperationMismatchMetricRecorder$Operation"],"web/monitoring/HttpMetricContract":["web/monitoring/HttpMetricContract","web/monitoring/HttpMetricContract$Labels","web/monitoring/HttpMetricContract$Method","web/monitoring/HttpMetricContract$Metric","web/monitoring/HttpMetricContract$Route","web/monitoring/HttpMetricContract$Status"]}
COUNTS={'GeneratedMetricValueContractTest':8,'GeneratedWebValueContractTest':4}
PINS={'GeneratedMetricValueContractTest':'c288800a2bf8b2d12c31a2879ce6d8e3fe6c89ba6a2bce6578a617b5c2569531','GeneratedWebValueContractTest':'fb18a92fa2c297a4b5e2513bd06a2f443da43bc4c2826b93762c3cad989f938b'}
TESTS={name:run.host.ROOT/('src/schubert-nk-'+module+'/src/test/java/'+PREFIX+module+'/monitoring/'+name+'.java') for name,module in [('GeneratedMetricValueContractTest','api'),('GeneratedWebValueContractTest','web')]}
FIXTURES={}
SESSION='PG15820-GENERATED-METRIC-VALUE-WHOLE12'
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
def module(name):
    value=name.split('/')[0]
    assert value in {'api','web'}
    return value
def main_path(name):return 'src/schubert-nk-'+module(name)+'/src/main/java/'+PREFIX+name+'.java'
if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg15820-generated-metric-value-twelve-pt-v1';run.OUT=run.host.BASE/'PG15820-generated-metric-value-twelve-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/GeneratedMetricValueTwelveJunitLauncher.java'
    run.NEW_TEST=TESTS['GeneratedWebValueContractTest'];run.TEST_ROOT=run.NEW_TEST.parent
    run.TEST_SOURCE_OVERRIDES={'GeneratedMetricValueContractTest':TESTS['GeneratedMetricValueContractTest']}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    assert run.host.sha(run.HELPER)=="0e277274f47b0da2c1ae66f2b3542a596f66f3404da812d43243537d00cd10b2"
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    old=data.read_checked(data.BASE/'PG15810-current2031-web-identity-registry-v1/manifest.json','49c59a5f449b1da48a00abd6461db5deda2ee9e64b98029c03201fd199d9416b')
    for name,path in TESTS.items():
        relative=str(path.relative_to(run.host.ROOT));text=path.read_text()
        assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'(?m)^  void [A-Za-z0-9_]+\(',text))==COUNTS[name]
        assert not any(v in text for v in ['@BeforeAll','@BeforeEach','@Disabled','ProcessBuilder','Files.','DriverManager','getConnection(','TemporaryInfrastructureException','Class.forName','HttpClient','createConnection(','new DbPoolMetricRecorder(','new OutboxRowsMetricRecorder(','new AsyncJobMetricRecorder(','new OperationMismatchMetricRecorder(','new HttpMetricContract('])
        suite=PREFIX.replace('/','.')+('api' if name=='GeneratedMetricValueContractTest' else 'web')+'.monitoring.'+name
        assert suite not in old['suiteNames']
    for name,pin in MAINS.items():
        full=PREFIX+name;path=main_path(name)
        assert old['fullSourceUnits'][full]['four100'] is True
        assert normal['begin']['inputHashes'][path]==run.host.sha(run.host.ROOT/path)==run.host.sha(COMPILE/'snapshot'/path)==pin
        with zipfile.ZipFile(normal['jars'][module(name)]['path']) as jar:
            assert {n[:-6] for n in jar.namelist() if n==full+'.class' or n.startswith(full+'$') and n.endswith('.class')}==set(old['fullSourceUnits'][full]['physical'])=={PREFIX+n for n in CLOSURES[name]}
    run.step=environmental_step;run.main()
