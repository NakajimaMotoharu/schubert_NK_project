"""Fixed collector source normal six Main/Test compilation only."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='e5436474218128d360ff63770f02c6afbd95020a'
SLOT=stage.host.W/'pg7876-api-query-collection-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7876-api-query-collection-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
