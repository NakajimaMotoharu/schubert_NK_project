"""Single fresh exec of whole Snapshot10/HeldState9/Artemis4, value-only contracts."""
import re
import snapshot_program_qualified_v2 as cfg
import scoped_prometheus_host as run

SOURCE = cfg.SOURCE
COMPILE = cfg.NORMAL_SLOT
COUNTS = cfg.COUNTS
SESSION = 'PG13842-SNAPSHOT-PROGRAM-WHOLE23'
TESTS = {name:cfg.data.ROOT/(cfg.TEST_ROOT+name+'.java') for name in COUNTS}
REPORTER = cfg.data.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
FIXTURE = 'src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt'
GOLDEN_SHA = '2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6'

def main():
    n,normal_pin = cfg.normal()
    static_path = cfg.out(cfg,13838)/'manifest.json'
    static = cfg.data.read_checked(static_path,cfg.data.sha(static_path.read_bytes()))
    source_path = cfg.data.BASE/'PG13840-snapshot-program-source-post-v1/manifest.json'
    source = cfg.data.read_checked(source_path,cfg.data.sha(source_path.read_bytes()))
    assert static['source'] == source['source'] == SOURCE and static['actualExit'] == source['actualExit'] == 0
    assert static['fullPhysicalMain'] == source['mainPhysical'] == 1843 and source['aliasNegativeVectors'] == 4
    assert static['currentBugs'] == static['currentMissingClasses'] == static['currentAnalysisErrors'] == 0
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = normal_pin
    run.SLOT = run.host.W/'pg13842-snapshot-program-whole-pt-v1'
    run.OUT = run.host.BASE/'PG13842-snapshot-program-whole-pt-v1'
    run.HELPER = cfg.data.ROOT/'tools/quality/architecture/InspectorSnapshotQualifiedProgramJunitLauncher.java'
    run.NEW_TEST = TESTS['InspectorUnitSnapshotTest']
    run.TEST_SOURCE_OVERRIDES = {name:p for name,p in TESTS.items() if p != run.NEW_TEST}
    run.EXTRA_TEST_SOURCES = (REPORTER,)
    run.FIXTURES = {FIXTURE:GOLDEN_SHA}
    run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    proof = cfg.data.read_checked(cfg.data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        assert run.host.sha(path) == cfg.PINS[name] == n['begin']['inputHashes'][str(path.relative_to(cfg.data.ROOT))]
        text = path.read_text()
        assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','DriverManager','ProcessBuilder','setAccessible','RootStartupContext','TemporaryInfrastructureException','WebStartupException','NativeReader','MaintenanceOwnerFrame'])
    config = COMPILE/'snapshot'/cfg.CONFIG
    assert n['begin']['inputHashes'][cfg.CONFIG] == run.host.sha(config) == cfg.CONFIG_SHA
    helper = run.HELPER.read_text()
    assert str(COMPILE/'snapshot') in helper
    for name,count in COUNTS.items():
        assert '"dev.codex.schubert.nk.batch.platform.'+name+'", '+str(count) in helper
    try:
        run.main()
    finally:
        assert run.host.sha(config) == cfg.CONFIG_SHA

if __name__ == '__main__':main()
