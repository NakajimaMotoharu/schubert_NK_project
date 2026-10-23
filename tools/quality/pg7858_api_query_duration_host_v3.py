"""Necessary fixed fixture/source138; previous two failures preserved."""
import pg7844_api_query_duration_host_v2 as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner
SLOT=runner.host.W/'pg7858-api-query-duration-host-v3'
POM=previous.POM
SUITES=previous.SUITES
DEPENDENCIES=previous.DEPENDENCIES
if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
