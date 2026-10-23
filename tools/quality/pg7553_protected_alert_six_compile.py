"""Current corrected-oracle source normal six compile; retain old9c compile as historical/PT0."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='3a863d360489cc2b09b4e1287b6469d4740eedf2'
SLOT=stage.host.W/'pg7553-protected-alert-six-compile-v2'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7553-protected-alert-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
