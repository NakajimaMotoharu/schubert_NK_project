"""Current122 ordinary API cases; supplied delivery observations only, no actual JMS/redelivery."""
import pg7658_mq_pressure_host_v2 as previous
import pg7006_monitoring_pure_host as runner

SLOT=runner.host.W/'pg7674-mq-redelivery-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.MqRedeliveryMetricRecorderTest')
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    previous.previous.previous.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
