"""Current130 ordinary API cases, borrowed owned Function/SDK fixtures only, no actual broker source."""
import pg7674_mq_redelivery_host as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner

SLOT=runner.host.W/'pg7690-mq-pressure-connection-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.MqPressureMetricCollectorTest')
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
