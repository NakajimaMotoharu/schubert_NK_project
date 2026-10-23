"""Fixed source normal six Main/Test package; actual broker/Root/native tests never invoked."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='153b3f3825d470bf15f7e5462e7b0beae199f76e'
SLOT=stage.host.W/'pg7694-mq-pressure-connection-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7694-mq-pressure-connection-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
