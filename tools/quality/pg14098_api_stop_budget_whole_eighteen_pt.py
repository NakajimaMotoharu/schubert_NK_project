"""Original whole18 with literal supplied clocks, no runtime hook/TERM/service operation."""
import re
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='0061d178cda80c2ce3926290619c64db125dbcfc'
COMPILE=run.host.W/'pg13832-snapshot-program-six-compile-v1'
COMPILE_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
COUNTS={'ApiStopBudgetTest':18}
SESSION='PG14098-API-STOP-BUDGET-CURRENT-WHOLE18'
ROOT=run.host.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap'
TESTS={name:ROOT/(name+'.java') for name in COUNTS}
PINS={'ApiStopBudgetTest':'50062a11dda9bac2eac52fa71a92ab75cd8b8bcbcd499c2f1a8fb8c077fcb15c'}
REPORTER=run.host.ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'

if __name__=='__main__':
    run.SOURCE=SOURCE;run.COMPILE=COMPILE;run.COMPILE_SHA=COMPILE_SHA
    run.SLOT=run.host.W/'pg14098-api-stop-budget-whole-eighteen-pt-v1'
    run.OUT=run.host.BASE/'PG14098-api-stop-budget-whole-eighteen-pt-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/ApiStopBudgetCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ApiStopBudgetTest'];run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,);run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12
    assert run.host.sha(REPORTER)==proof['toolSourceHashes'][str(REPORTER)]=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    text=TESTS['ApiStopBudgetTest'].read_text();assert run.host.sha(TESTS['ApiStopBudgetTest'])==PINS['ApiStopBudgetTest']
    assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+[A-Za-z0-9_]+\s*\(',text))==18
    assert not any(term in text for term in ['@BeforeAll','@BeforeEach','ProcessBuilder','DriverManager','Files.','Linux','TemporaryInfrastructureException','getenv(','ApiProcessLifetime','addShutdownHook'])
    assert '"dev.codex.schubert.nk.api.bootstrap.ApiStopBudgetTest", 18' in run.HELPER.read_text()
    run.main()
