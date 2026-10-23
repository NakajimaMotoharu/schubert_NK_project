"""Normal six Main/Test compile/package only, no outbox DB/dispatcher/Root operation."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as host

SOURCE='dbb794ec157bcdab86a3e0684e51562648bdd7ae'
SLOT=stage.host.W/'pg7394-api-outbox-rows-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7394-api-outbox-rows-six-compile-v1'
    stage.DEPENDENCY_JARS=host.DEPENDENCIES
    stage.main()
