"""Current174 ordinary cases, preserving prior compile-only failures as distinct sources."""
import pg7978_exact_duration_host as previous
import pg7628_api_inbox_replay_host as dependency
import pg7006_monitoring_pure_host as runner
SLOT=runner.host.W/'pg8006-exact-duration-host-v3'
POM=previous.POM
SUITES=previous.SUITES
DEPENDENCIES=previous.DEPENDENCIES
if __name__=='__main__':
    dependency.verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
