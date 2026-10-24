"""Original API owner-before-GC-activation14, fresh own JVM only."""
import scoped_prometheus_host as run
import re

SOURCE = 'e027929a7a6da504e0d03efd517ea98656ce369b'
COMPILE = run.host.W / 'pg8566-api-system-six-compile-v1'
COMPILE_SHA = 'a5c9cc24d4c0f5663ac7d79f66f254dc95dc507bbefc6208b633687a0f11d522'
COUNTS = {'ApiSystemMetricsTest': 14}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8568-api-system-host-v1'
    run.OUT = run.host.BASE / 'PG8568-api-system-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiSystemMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiSystemMetricsTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8568-API-SYSTEM'
    run.FIXTURES = {}
    selection = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);', run.HELPER.read_text(), flags=re.S)
    run.require(len(selection) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"', selection[0]) == ['dev.codex.schubert.nk.api.monitoring.ApiSystemMetricsTest'], 'exact new system fixture selected before original JVM')
    run.main()
