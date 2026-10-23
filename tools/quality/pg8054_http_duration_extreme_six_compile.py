"""Fixed new one-oracle source normal six compile and exact classpath metadata, PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='7e57c7ace25f19a20012019768daca1844861b85'
SLOT=stage.host.W/'pg8054-http-duration-extreme-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8054-http-duration-extreme-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
