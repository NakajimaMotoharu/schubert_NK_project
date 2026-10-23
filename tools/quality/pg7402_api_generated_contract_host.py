"""BUG1660: actual72 ordinary API cases including generated-value contracts; no actual runtime actions."""
import pg7006_monitoring_pure_host as runner
import pg7390_api_outbox_rows_host as previous

SLOT=runner.host.W/'pg7402-api-generated-contract-host-v1'
POM=previous.POM
SUITES=previous.SUITES+('dev.codex.schubert.nk.api.monitoring.GeneratedMetricValueContractTest',)
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
