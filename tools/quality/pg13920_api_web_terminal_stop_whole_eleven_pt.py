"""Original whole11 memory callbacks/argv rejection, never actual terminal capture/stop."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE = run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA = '8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS = {'ApiTerminalCaptureTest':3,'WebTerminalCaptureTest':3,'WebRuntimeStopTest':5}
SESSION = 'PG13920-API-WEB-TERMINAL-STOP-MEMORY-CURRENT-WHOLE11'
ROOT = run.host.ROOT
TESTS = {name:ROOT/('src/schubert-nk-'+('api' if name.startswith('Api') else 'web')+'/src/test/java/dev/codex/schubert/nk/'+('api' if name.startswith('Api') else 'web')+'/bootstrap/'+name+'.java') for name in COUNTS}
PINS = {'ApiTerminalCaptureTest':'b3d30d3a406c41637613154913d115085f9007f1157189e876417ea831232686',
    'WebTerminalCaptureTest':'d5c8c512c291b011e4cc82b699d0782423bc27da57f79fa9150283ed76fe1dc4',
    'WebRuntimeStopTest':'d38668723e67f81c94c184dde8a960f44aa9056b75814df3fc8d90653a75f55c'}
REPORTER = ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__ == '__main__':
    run.SOURCE = SOURCE;run.COMPILE = COMPILE;run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W/'pg13920-api-web-terminal-stop-whole-eleven-pt-v1'
    run.OUT = run.host.BASE/'PG13920-api-web-terminal-stop-whole-eleven-pt-v1'
    run.HELPER = ROOT/'tools/quality/architecture/ApiWebTerminalStopMemoryJunitLauncher.java'
    run.NEW_TEST = TESTS['ApiTerminalCaptureTest']
    run.TEST_SOURCE_OVERRIDES = {n:p for n,p in TESTS.items() if n != run.NEW_TEST.stem}
    run.EXTRA_TEST_SOURCES = (REPORTER,);run.FIXTURES = {};run.COUNTS = COUNTS;run.SESSION_ID = SESSION
    assert str(run.AGENT).startswith(str(run.host.TC)+'/m2/') and not str(run.AGENT).startswith('/opt/pgpt-tools-pg390/')
    proof = data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit'] == proof['productTestsExecuted'] == 0 and proof['toolChecksIndependentlyConfirmed'] == 12
    assert run.host.sha(REPORTER) == proof['toolSourceHashes'][str(REPORTER)] == 'c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    for name,path in TESTS.items():
        text = path.read_text();assert run.host.sha(path) == PINS[name]
        assert text.count('@Test') == len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text)) == COUNTS[name]
        assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','new ApiProcessMain()','new WebProcessMain()','new String[0]'])
        assert '"dev.codex.schubert.nk.'+('api' if name.startswith('Api') else 'web')+'.bootstrap.'+name+'", '+str(COUNTS[name]) in run.HELPER.read_text()
    run.main()
