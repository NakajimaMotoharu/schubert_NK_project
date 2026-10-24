"""New Gauge16 and actual precision-Web6, one original22/2 exec, no historical PASS replay."""
import scoped_prometheus_host as run

SOURCE = 'e1ba2ccc51f1f24bd48d74e3b906b48489473a39'
COMPILE = run.host.W / 'pg8350-web-gauge-six-compile-v1'
COMPILE_SHA = '62abed6fa1b60fd22df54f575562c476423376acc43f4155798107c26697b05b'
COUNTS = {'WebGaugeMetricExporterTest': 16, 'WebGaugeExporterContractTest': 6}

if __name__ == '__main__':
    run.SOURCE = SOURCE
    run.COMPILE = COMPILE
    run.COMPILE_SHA = COMPILE_SHA
    run.SLOT = run.host.W / 'pg8352-web-gauge-host-v1'
    run.OUT = run.host.BASE / 'PG8352-web-gauge-host-v1'
    run.HELPER = run.host.ROOT / 'tools/quality/architecture/WebGaugeExporterJunitLauncher.java'
    run.NEW_TEST = run.host.ROOT / 'tools/quality/architecture/WebGaugeExporterContractTest.java'
    run.COUNTS = COUNTS
    run.SESSION_ID = 'PG8352-WEB-GAUGE'
    run.FIXTURES = {}
    run.main()
