"""Fixed query duration source normal six Main/Test compilation; PT0, no DB/Root operations."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='a2d196d88d4c1eab6f045a035eb9005d7e0e442c'
SLOT=stage.host.W/'pg7834-api-query-duration-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7834-api-query-duration-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
