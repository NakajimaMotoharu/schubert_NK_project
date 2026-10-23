"""Current fixed source normal six compilation only; PT0 remains UNRUN."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk
SOURCE='ded75f5bd119088601d881df1b571c297f440278'
SLOT=stage.host.W/'pg8010-exact-duration-six-compile-v3'
if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8010-exact-duration-six-compile-v3'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
