"""Fixed Web pool three-program source normal six compile/NullAway/classpath, PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='e196d0816c8a4920696d4f601f8b4cf97e9e8b48'
SLOT=stage.host.W/'pg8122-web-pool-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8122-web-pool-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
