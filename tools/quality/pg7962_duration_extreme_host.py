"""Current164 ordinary API cases; only two added fixed scalar histogram sequence oracles."""
import pg7912_mq_event_host as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner
SLOT=runner.host.W/'pg7962-duration-extreme-host-v1'
POM=previous.POM
SUITES=previous.SUITES
DEPENDENCIES=previous.DEPENDENCIES
if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
