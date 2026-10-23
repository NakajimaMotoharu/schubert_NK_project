"""Fixed test-only source normal six Main/Test compilation, no PT/Root/runtime operations."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='0b78d18f241ca0f8c0f7bc48e8b9b80deb163544'
SLOT=stage.host.W/'pg7966-duration-extreme-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7966-duration-extreme-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
