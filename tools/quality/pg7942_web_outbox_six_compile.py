"""Fixed Web outbox source normal six Main/Test compile and reviewed classpath metadata, PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='f84acdd7d3b146c3cf6171cfabe66e4d18e35a82'
SLOT=stage.host.W/'pg7942-web-outbox-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7942-web-outbox-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()
