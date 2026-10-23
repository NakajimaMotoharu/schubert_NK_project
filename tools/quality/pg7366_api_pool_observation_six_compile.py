"""Normal six Main/Test compile/package only with exact existing Hikari/SLF4J auxiliary pins."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as host

SOURCE='e87468fac255512460f743392d36b1fecb361e05'
SLOT=stage.host.W/'pg7366-api-pool-observation-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7366-api-pool-observation-six-compile-v1'
    stage.DEPENDENCY_JARS=host.DEPENDENCIES
    stage.main()
