"""BUG1660 Test-only fixed source normal six Main/Test compile/package, not actual runtime operations."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as host

SOURCE='fcedc05b1b61b74b6b8a3fe3d9e5ea8d19859650'
SLOT=stage.host.W/'pg7406-api-generated-contract-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7406-api-generated-contract-six-compile-v1'
    stage.DEPENDENCY_JARS=host.DEPENDENCIES
    stage.main()
