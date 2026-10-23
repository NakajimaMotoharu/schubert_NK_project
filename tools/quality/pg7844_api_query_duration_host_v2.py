"""Necessary changed-source138 ordinary API cases; preserve original7830 failure unchanged."""
import pg7830_api_query_duration_host as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner
SLOT=runner.host.W/'pg7844-api-query-duration-host-v2'
POM=previous.POM
SUITES=previous.SUITES
DEPENDENCIES=previous.DEPENDENCIES
if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
