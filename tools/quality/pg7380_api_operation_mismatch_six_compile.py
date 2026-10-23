"""Normal six Main/Test compile/package only, not real mismatch/authentication/Root operation."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as host

SOURCE='40cf5c309cd2e2c54f7be6904ff4354ff3e32acf'
SLOT=stage.host.W/'pg7380-api-operation-mismatch-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7380-api-operation-mismatch-six-compile-v1'
    stage.DEPENDENCY_JARS=host.DEPENDENCIES
    stage.main()
