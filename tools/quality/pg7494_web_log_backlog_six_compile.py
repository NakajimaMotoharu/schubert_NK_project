"""Fixed-source normal six Main/Test compile/package; PT0 and no runtime/DB/Root invocation."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='3174583f445581e120f855ec5065d9f88e5ca617'
SLOT=stage.host.W/'pg7494-web-log-backlog-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7494-web-log-backlog-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
