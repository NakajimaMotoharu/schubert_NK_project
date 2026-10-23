"""Fixed public Timer-composition candidate normal six compile/classpath, PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='d921f49a3b6ed0219e6e10d65198d774f37ae9a6'
SLOT=stage.host.W/'pg8080-http-duration-composition-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8080-http-duration-composition-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
