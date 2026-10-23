"""Changed-source ordinary synthetic Batch regression, protected alerts cannot auto-close."""
import pg7006_monitoring_pure_host as runner
import pg7532_async_byte_unit_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7548-protected-alert-host-v1'
SUITES=previous.SUITES

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
