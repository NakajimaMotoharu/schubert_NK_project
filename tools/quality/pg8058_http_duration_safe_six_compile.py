"""Fixed HTTP timer-correction source normal six compile and classpath metadata, PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='27324ee12173955ff7bace340c99dd36a891d324'
SLOT=stage.host.W/'pg8058-http-duration-safe-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8058-http-duration-safe-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
