"""Fixed source normal six Main/Test compile/package, no runtime/DB/Root tests."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='8c538b33f4a25acdfad195d2dee44d6d783ac6e9'
SLOT=stage.host.W/'pg7632-api-inbox-replay-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7632-api-inbox-replay-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
