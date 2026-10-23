"""Exact current source normal six Main/Test compilation only, no PT/actual operations."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='1540267d33d2cbe93b7d7ec9f917df78a54ac3be'
SLOT=stage.host.W/'pg7862-api-query-duration-six-compile-v3'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7862-api-query-duration-six-compile-v3'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
