"""Fixed source normal six Main/Test package; no real retention/runtime/Root tests."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='323925a4218ae20c41a3fa93f1846b73dd038a5a'
SLOT=stage.host.W/'pg7714-observed-retention-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7714-observed-retention-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
