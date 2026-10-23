"""Current146 ordinary API cases, borrowed complete observations only."""
import pg7858_api_query_duration_host_v3 as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner
SLOT=runner.host.W/'pg7872-api-query-collection-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricCollectorTest')
DEPENDENCIES=previous.DEPENDENCIES
if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
