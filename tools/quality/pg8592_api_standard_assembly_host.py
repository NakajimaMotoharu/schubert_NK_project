"""Original API owner-before-GC-activation14, fresh own JVM only."""
import scoped_prometheus_host as run
import re

SOURCE = '86ec58d4f8d11350c01d62a5fab0be8a9f1ba670'
COMPILE = run.host.W / 'pg8590-api-standard-assembly-six-compile-v1'
COMPILE_SHA = 'd7511aef567be7eb5e78f7406db152928949f8f42e10a65e04d7f13ad5161dce'
COUNTS = {'ApiStandardMetricsTest': 13}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8592-api-standard-assembly-host-v1'
    run.OUT = run.host.BASE / 'PG8592-api-standard-assembly-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/ApiStandardMetricsJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricsTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8592-API-STANDARD'
    run.FIXTURES = {}
    selection = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);', run.HELPER.read_text(), flags=re.S)
    run.require(len(selection) == 1 and re.findall(r'"([a-zA-Z0-9_.]+)"', selection[0]) == ['dev.codex.schubert.nk.api.monitoring.ApiStandardMetricsTest'], 'exact new system fixture selected before original JVM')
    run.main()
