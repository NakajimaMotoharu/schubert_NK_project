"""Fixed restart source normal six Main/Test package; PT0, no actual process/Root operations."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='3751f2150898ddd0ff939571f99e13c888e17653'
SLOT=stage.host.W/'pg7818-restart-metric-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7818-restart-metric-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
