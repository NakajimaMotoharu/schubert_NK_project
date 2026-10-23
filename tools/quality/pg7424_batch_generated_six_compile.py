"""Test-only source change: normal six Main/Test compile, PT explicitly unrun here."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='9d8e520376501de825f26f963d6914beb98b890c'
SLOT=stage.host.W/'pg7424-batch-generated-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7424-batch-generated-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
