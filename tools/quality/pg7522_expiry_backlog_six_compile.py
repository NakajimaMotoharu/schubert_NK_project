"""Fixed source normal six Main/Test compile/package only, no real queue/purge/native tests."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='6247ebe6024ae25fd581b122a14abe4e0f5dec80'
SLOT=stage.host.W/'pg7522-expiry-backlog-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7522-expiry-backlog-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
