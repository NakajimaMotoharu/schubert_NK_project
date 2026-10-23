"""Actual56 SDK/fake-interface API cases, enum-only mismatch observations/no token/key/auth use."""
import pg7006_monitoring_pure_host as runner
import pg7362_api_pool_observation_host as previous

SLOT=runner.host.W/'pg7376-api-operation-mismatch-host-v1'
POM=previous.POM
SUITES=previous.SUITES+('dev.codex.schubert.nk.api.monitoring.OperationMismatchMetricRecorderTest',)
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
