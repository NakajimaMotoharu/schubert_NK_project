"""Fixed nullable-result composition source, normal six compile/NullAway/classpath; PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='731d84d79fb44857dab999ef380f49d3d86ac375'
SLOT=stage.host.W/'pg8098-http-duration-nullable-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8098-http-duration-nullable-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
