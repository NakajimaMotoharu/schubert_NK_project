"""Corrected Test source, fixed normal six Main/Test package, PT0; no probes/Root."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='5ac3d6a18d8c3ed4c6c5a0c70466b9f8d4553340'
SLOT=stage.host.W/'pg7804-integrity-metric-six-compile-v2'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7804-integrity-metric-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
