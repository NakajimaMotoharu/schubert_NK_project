"""Fixed source normal six Main/Test package plus reviewed classpath metadata, PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='047947f498a72d81eb3441e8fc56870f8ba5d9b4'
SLOT=stage.host.W/'pg7754-media-collector-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7754-media-collector-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()

