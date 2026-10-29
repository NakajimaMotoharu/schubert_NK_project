"""Original whole22 closed policy/registry/status/missing memory contracts, no actual target."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={"MonitoringPolicyEngineTest":9,"AlertRegistryTest":4,"MonitoringStatusTextTest":6,"MonitoringMissingObservationTest":3}
SESSION='PG14152-POLICY-REGISTRY-STATUS-MISSING-CURRENT-WHOLE22'
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={"MonitoringPolicyEngineTest":"64b3ee74b7b5f66464594169332d5806ec7f77436c2797fe76607bcc7d6562d9","AlertRegistryTest":"cda14d500331e2ca2b92e6308fb325c65c8bd9ea81da012cecc709533fcd66d8","MonitoringStatusTextTest":"4b083f731a9c47f9d860fc4887ddfde17cd8bb842864d20efd0bca5c8df3f34c","MonitoringMissingObservationTest":"64bfbd2e4fd2f43d20097e81070629d6af8993323aeb88511f639ef2840ae677"}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14152-policy-registry-status-missing-whole-twenty-two-pt-v1'
    run.OUT=run.host.BASE/'PG14152-policy-registry-status-missing-whole-twenty-two-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/PolicyRegistryCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MonitoringPolicyEngineTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text=path.read_text();assert run.host.sha(path)==PINS[name]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','import java.sql','ManagementFactory'])
        assert '"dev.codex.schubert.nk.batch.monitoring.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
