"""Fixed media byte source normal six compile-package and reviewed metadata; PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='082429175a7c64abd86c8dccca2f8f9be97fdc4a'
SLOT=stage.host.W/'pg7784-media-bytes-six-compile-v2'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7784-media-bytes-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()
