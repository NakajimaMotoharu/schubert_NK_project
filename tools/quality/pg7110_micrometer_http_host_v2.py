"""New15-case original after test-only AutoCloseable fixture correction, no repeated completed PT."""
import pg7006_monitoring_pure_host as runner
import pg7106_micrometer_http_host as original

SLOT=runner.host.W/'pg7110-micrometer-http-host-v2'
SUITES=original.SUITES


if __name__=='__main__':
    runner.POM=original.POM
    runner.DEPENDENCY_JARS=original.SDK
    runner.main(SLOT,SUITES)
