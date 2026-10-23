"""Same fixed source normal six Main/Test package; ordinary runtime/native tests not selected."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='a1c1cbe2975c04a767ff13ea5f3141640a8f7b3d'
SLOT=stage.host.W/'pg7678-mq-redelivery-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7678-mq-redelivery-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
