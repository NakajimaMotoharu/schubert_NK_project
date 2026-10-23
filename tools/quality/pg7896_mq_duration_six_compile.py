"""Fixed MQ duration source normal six Main/Test compilation only."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='602808269ee90b4ee5c388e7bc6f4bf7af846fd7'
SLOT=stage.host.W/'pg7896-mq-duration-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7896-mq-duration-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
