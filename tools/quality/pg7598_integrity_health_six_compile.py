"""Fixed source normal six compile/package, no actual integrity/Root/native operation or PT."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='676b954e73369850e88fb575c3744b08c8c4c1fd'
SLOT=stage.host.W/'pg7598-integrity-health-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7598-integrity-health-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
