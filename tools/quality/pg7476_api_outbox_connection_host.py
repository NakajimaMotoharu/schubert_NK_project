"""Current98 ordinary API cases; new read-close-publication uses owned JDBC/SDK fixtures only."""
import pg7006_monitoring_pure_host as runner
import pg7462_api_outbox_repository_host as previous

SLOT=runner.host.W/'pg7476-api-outbox-connection-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.OutboxMetricCollectorTest')
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
