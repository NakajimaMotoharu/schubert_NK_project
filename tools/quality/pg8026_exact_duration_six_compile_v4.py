"""Fixed final-registry candidate normal six compile; no PT or actual services."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='6c6ba4ab5058b22847d6dee4945bb7c22a33d48c'
SLOT=stage.host.W/'pg8026-exact-duration-six-compile-v4'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8026-exact-duration-six-compile-v4'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
