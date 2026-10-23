"""Changed-source ordinary Batch regression; BUG1665 byte/count unit correction, no real I/O."""
import pg7006_monitoring_pure_host as runner
import pg7518_expiry_backlog_host as previous
import pg7106_micrometer_http_host as sdk

SLOT=runner.host.W/'pg7532-async-byte-unit-host-v1'
SUITES=previous.SUITES

if __name__=='__main__':
    runner.DEPENDENCY_JARS=sdk.SDK
    runner.main(SLOT,SUITES)
