"""Web HTTP label metadata six tests, no existing DB fixture or target operations."""
import pg7006_monitoring_pure_host as runner

SLOT=runner.host.W/'pg7094-web-http-metric-host-v1'
POM='tools/quality/harnesses/monitoring-web-http-pom.xml'
SUITE='dev.codex.schubert.nk.web.monitoring.HttpMetricContractTest'


if __name__=='__main__':
    runner.POM=POM
    runner.main(SLOT,(SUITE,))
