"""New-only corrected oracle source, retain original7548/F2; do not rerun the old slot."""
import pg7006_monitoring_pure_host as runner
import pg7548_protected_alert_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7548-protected-alert-host-v2'
SUITES=previous.SUITES

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
