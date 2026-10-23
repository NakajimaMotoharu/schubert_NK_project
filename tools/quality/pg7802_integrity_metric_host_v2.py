"""Corrected253 ordinary Batch cases include independent original Repository BatchStep contract."""
import pg7788_integrity_metric_host as previous
import pg7006_monitoring_pure_host as runner
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7802-integrity-metric-host-v2'
SUITES=previous.SUITES

if __name__=='__main__':
    runner.POM='tools/quality/harnesses/monitoring-pom.xml'
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
