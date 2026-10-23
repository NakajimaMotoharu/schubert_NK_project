"""Fixed source normal six Main/Test compile/package; not actual production PT or DB operations."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='332f970a7461c5eace27d1da0c63bfb4c2852f0e'
SLOT=stage.host.W/'pg7466-api-outbox-repository-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7466-api-outbox-repository-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
