"""Corrected9e579a97a normal six Main/Test compilation; PT0 and no runtime operations."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='9e579a97a9846a5d45a67246b3cd6d53c3f9220d'
SLOT=stage.host.W/'pg7848-api-query-duration-six-compile-v2'
if __name__=='__main__':
    stage.SOURCE=SOURCE
    stage.SLOT=SLOT;stage.OUT=stage.host.BASE/'PG7848-api-query-duration-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
