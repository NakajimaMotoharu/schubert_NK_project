"""Current API eighty ordinary cases, supplied Duration data and owned SDK only."""
import pg7006_monitoring_pure_host as runner
import pg7402_api_generated_contract_host as previous

SLOT=runner.host.W/'pg7448-api-outbox-age-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.OutboxAgeMetricRecorderTest')
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
