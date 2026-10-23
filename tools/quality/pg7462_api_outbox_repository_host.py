"""Current90 ordinary API cases; owned JDBC proxy-only new ten, no DB/driver/runtime connection."""
import pg7006_monitoring_pure_host as runner
import pg7448_api_outbox_age_host as previous

SLOT=runner.host.W/'pg7462-api-outbox-repository-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest')
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
