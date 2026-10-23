"""BUG1670 fixed source ordinary114, original114/static finding retained, no business/runtime calls."""
import pg7644_mq_pressure_host as previous
import pg7006_monitoring_pure_host as runner

SLOT=runner.host.W/'pg7658-mq-pressure-host-v2'
POM=previous.POM
SUITES=previous.SUITES
DEPENDENCIES=previous.DEPENDENCIES

if __name__=='__main__':
    previous.previous.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
