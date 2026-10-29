"""Original whole33 supplied backlog/Backup observations, no actual broker or Backup operations."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={"AsyncQueueMonitorTest":9,"WebLogBacklogMonitorTest":8,"ExpiryBacklogMonitorTest":8,"BackupHealthMonitorTest":8}
SESSION='PG14158-SUPPLIED-BACKLOG-BACKUP-CURRENT-WHOLE33'
ROOT=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={"AsyncQueueMonitorTest":"7128ed500fce38c80558829fe62e7f7bf5309e9f5f933642b6f252c9796e8407","WebLogBacklogMonitorTest":"ba5578f1227f7349a0dc2cc6feba66e9c05d786acd6046329570e556050ffb26","ExpiryBacklogMonitorTest":"38761025731fef2a215b5f5d87db3bcfb51e2ed0b12f7faf421dc5218ce097a5","BackupHealthMonitorTest":"fa96ad8b693632dcf0040e5f0676d596f913822197ea22afaf85289251e09c33"}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14158-supplied-backlog-backup-whole-thirty-three-pt-v1'
    run.OUT=run.host.BASE/'PG14158-supplied-backlog-backup-whole-thirty-three-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/SuppliedBacklogCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['AsyncQueueMonitorTest'];run.TEST_ROOT=ROOT;run.TEST_SOURCE_OVERRIDES={}
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
