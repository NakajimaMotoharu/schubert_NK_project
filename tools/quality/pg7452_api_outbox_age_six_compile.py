"""Fixed source normal six Main/Test compile/package, not executed production PT."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='d6c7f61b542d8131d1d5c38cfb3dc03f6a471bc7'
SLOT=stage.host.W/'pg7452-api-outbox-age-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7452-api-outbox-age-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
