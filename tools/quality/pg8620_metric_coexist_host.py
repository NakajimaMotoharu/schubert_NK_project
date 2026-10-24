"""New actual same-registry standard-custom6/3, source unchanged and normal not replayed."""
import re
import scoped_prometheus_host as run

SOURCE = 'e81adb96849e4067beb12f212350ab4fbd4b1998'
COMPILE = run.host.W / 'pg8608-web-batch-standard-assembly-six-compile-v1'
COMPILE_SHA = '4033792b291efa7bbcb2403c4fdd81bd459c206d3b2bfe619e1488dff6bc44a3'
COUNTS = {'ApiMetricCoexistenceTest': 2, 'WebMetricCoexistenceTest': 2, 'BatchMetricCoexistenceTest': 2}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8620-metric-coexist-host-v1'
    run.OUT = run.host.BASE / 'PG8620-metric-coexist-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/MetricCoexistenceJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/ApiMetricCoexistenceTest.java'
    run.TEST_SOURCE_OVERRIDES = {name: run.host.ROOT / ('tools/quality/architecture/' + name + '.java') for name in ('WebMetricCoexistenceTest', 'BatchMetricCoexistenceTest')}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8620-METRIC-COEXIST'
    run.FIXTURES = {}
    selection = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);', run.HELPER.read_text(), flags=re.S)
    expected = {'dev.codex.schubert.nk.' + role + '.monitoring.' + title + 'MetricCoexistenceTest' for role, title in (('api', 'Api'), ('web', 'Web'), ('batch', 'Batch'))}
    run.require(len(selection) == 1 and len(re.findall(r'"([a-zA-Z0-9_.]+)"', selection[0])) == 3 and set(re.findall(r'"([a-zA-Z0-9_.]+)"', selection[0])) == expected, 'exact new three fixture FQCN selection')
    run.main()
