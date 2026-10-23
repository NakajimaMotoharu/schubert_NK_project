"""Fixed candidate normal six Main/Test compilation only, never a PT pass."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='fe9a02d0b9704be0bb2e8eecd2e886a49fad4ee3'
SLOT=stage.host.W/'pg7982-exact-duration-six-compile-v1'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7982-exact-duration-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
