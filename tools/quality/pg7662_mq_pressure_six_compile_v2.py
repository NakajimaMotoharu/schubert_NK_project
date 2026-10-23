"""BUG1670 fixed source normal six Main/Test compile/package, actual PT0/UNRUN."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='1cbd253172b836e059b94578000c553a197f5407'
SLOT=stage.host.W/'pg7662-mq-pressure-six-compile-v2'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7662-mq-pressure-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
