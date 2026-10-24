"""New actual standard-duration-ready pipeline4/2, source unchanged and normal not replayed."""
import re
import scoped_prometheus_host as run

SOURCE = 'f817b004781e6c32aa2d384dd12855cad7175ddc'
COMPILE = run.host.W / 'pg8632-api-web-custom-payload-six-compile-v1'
COMPILE_SHA = '8039af9b7750d5b689c4663cdb6f02634ad857ed76ad52f6f7d3bba25c0d1c9b'
COUNTS = {'ApiMetricPayloadPrecisionTest': 2, 'WebMetricPayloadPrecisionTest': 2}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8644-metric-payload-precision-host-v1'
    run.OUT = run.host.BASE / 'PG8644-metric-payload-precision-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/MetricPayloadPrecisionJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/ApiMetricPayloadPrecisionTest.java'
    run.TEST_SOURCE_OVERRIDES = {'WebMetricPayloadPrecisionTest': run.host.ROOT / 'tools/quality/architecture/WebMetricPayloadPrecisionTest.java'}
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8644-METRIC-PRECISION'
    run.FIXTURES = {}
    selection = re.findall(r'List<String>\s+types\s*=\s*List\.of\((.*?)\);', run.HELPER.read_text(), flags=re.S)
    expected = {'dev.codex.schubert.nk.' + role + '.monitoring.' + title + 'MetricPayloadPrecisionTest' for role,title in (('api','Api'),('web','Web'))}
    run.require(len(selection)==1 and len(re.findall(r'"([a-zA-Z0-9_.]+)"',selection[0]))==2 and set(re.findall(r'"([a-zA-Z0-9_.]+)"',selection[0]))==expected, 'exact new precision fixture FQCN selection')
    run.main()
