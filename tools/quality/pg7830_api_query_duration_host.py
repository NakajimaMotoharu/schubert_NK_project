"""Current138 ordinary API cases; numeric SDK observations and owned fixtures, no actual DB/clock."""
import pg7690_mq_pressure_connection_host as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner

SLOT=runner.host.W/'pg7830-api-query-duration-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorderTest')
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
