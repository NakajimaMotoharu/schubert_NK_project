"""BUG1698 corrected fixture, original same-source44/4, not replaying failed source."""
import pg8336_web_counter_host as previous

SOURCE = '6c91f378543e9c1cbfa0c8a9dd3115f91cbbdccb'
COMPILE = previous.run.host.W / 'pg8338-web-counter-fixed-six-compile-v1'
COMPILE_SHA = '8d4135584a58c820674879d539153abd3813a4b9bac6168284ab245cf07c3efe'
COUNTS = previous.COUNTS
FIXTURE, FIXTURE_SHA = previous.FIXTURE, previous.FIXTURE_SHA

if __name__ == '__main__':
    run = previous.run
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8340-web-counter-fixed-host-v1'
    run.OUT = run.host.BASE / 'PG8340-web-counter-fixed-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebCounterExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/WebCounterExporterContractTest.java'
    run.TEST_SOURCE_OVERRIDES = {'WebTimerExporterContractTest': run.host.ROOT / 'tools/quality/architecture/WebTimerExporterContractTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8340-WEB-COUNTER'
    run.FIXTURES = {FIXTURE: FIXTURE_SHA}
    run.main()
