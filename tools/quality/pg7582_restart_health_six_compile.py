"""Fixed source normal six Main/Test compile; business/Root/native PT explicitly unrun."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='9f7697a28e9ae5a55713eeb69a4a3a90d00a41cd'
SLOT=stage.host.W/'pg7582-restart-health-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7582-restart-health-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
