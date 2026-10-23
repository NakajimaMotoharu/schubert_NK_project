"""Actual64 ordinary API SDK/fake-interface cases; supplied row counts only, no outbox/DB actions."""
import pg7006_monitoring_pure_host as runner
import pg7376_api_operation_mismatch_host as previous

SLOT=runner.host.W/'pg7390-api-outbox-rows-host-v1'
POM=previous.POM
SUITES=previous.SUITES+('dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorderTest',)
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
