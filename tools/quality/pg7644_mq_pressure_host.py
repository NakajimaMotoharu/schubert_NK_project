"""Current114 ordinary API cases; only supplied MQ samples and owned SDK, never broker/JMS."""
import pg7628_api_inbox_replay_host as previous
import pg7006_monitoring_pure_host as runner

SLOT=runner.host.W/'pg7644-mq-pressure-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.MqPressureMetricRecorderTest')
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    previous.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
