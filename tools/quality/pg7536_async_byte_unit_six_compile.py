"""Fixed changed source normal six-module compile/package; all business PT explicitly unrun."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='8f6b3bff2845ce99276dfb56046a473f7715e4f6'
SLOT=stage.host.W/'pg7536-async-byte-unit-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7536-async-byte-unit-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
