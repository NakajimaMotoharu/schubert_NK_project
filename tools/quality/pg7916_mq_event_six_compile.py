"""Fixed MQ event source normal six Main/Test compilation, PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='23b74be401690ecb0f0007a66869c4ea2a699b02'
SLOT=stage.host.W/'pg7916-mq-event-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7916-mq-event-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
