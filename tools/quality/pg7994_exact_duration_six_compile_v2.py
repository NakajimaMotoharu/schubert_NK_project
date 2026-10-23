"""Normal six source/Test compilation for fixed candidate, PT0 not a pass."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='9fddbd402c394269f35f0a50975bcdf5976abb89'
SLOT=stage.host.W/'pg7994-exact-duration-six-compile-v2'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7994-exact-duration-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
