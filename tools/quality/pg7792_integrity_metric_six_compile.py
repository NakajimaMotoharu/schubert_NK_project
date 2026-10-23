"""Fixed source normal six Main/Test package; no actual integrity/Root tests."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='f9d91150a9d82cd3edecbc02043c946926389967'
SLOT=stage.host.W/'pg7792-integrity-metric-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7792-integrity-metric-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
