"""Fixed media byte source normal six compile-package and reviewed metadata; PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='b3662200b19484f1f392b22a3f69ade3d9e1c300'
SLOT=stage.host.W/'pg7770-media-bytes-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7770-media-bytes-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()
