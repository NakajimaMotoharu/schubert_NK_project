"""Fixed source normal six Main/Test compile-package only, no real DLQ/Root/native PT."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='cfd8c12ddfeb6be74b41029478c4df76b124ccfe'
SLOT=stage.host.W/'pg7614-dlq-health-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7614-dlq-health-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
