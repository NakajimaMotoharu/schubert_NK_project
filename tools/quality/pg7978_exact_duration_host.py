"""Same-source ordinary174/21: exact finite duration registry and regression, no actual services."""
import pg7962_duration_extreme_host as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner
SLOT=runner.host.W/'pg7978-exact-duration-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.ExactDurationMeterRegistryTest')
DEPENDENCIES=previous.DEPENDENCIES
if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
