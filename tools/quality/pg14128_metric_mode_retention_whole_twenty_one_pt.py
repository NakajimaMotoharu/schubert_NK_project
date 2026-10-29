"""Original whole6/7/8 value contracts with one closed independent public TSV resource."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={'MetricContractTest':6,'MonitoringModePolicyTest':7,'MonitoringRetentionConfigurationTest':8}
SESSION='PG14128-METRIC-MODE-RETENTION-CURRENT-WHOLE21'
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'MetricContractTest':'29605f7776c85226dd130a55a06b7e9f17f6e7f8799915c7ec2ecab602c61f84','MonitoringModePolicyTest':'525d72e00ac97b3510537e62426e91f25e0129f3d8812e34380f1efda4b4663c','MonitoringRetentionConfigurationTest':'34c225d054f02940c9b2c9f8a7e1825f5c189389e089c9b40a0298dcc49bd8ab'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
FIXTURE='src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv'
FIXTURE_SHA='1447faabc6f056120561e4356dd75696ace4df613b6379246af29f9837fc43dc'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14128-metric-mode-retention-whole-twenty-one-pt-v1'
    run.OUT=run.host.BASE/'PG14128-metric-mode-retention-whole-twenty-one-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/MetricModeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MetricContractTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={FIXTURE:FIXTURE_SHA};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory'])
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
