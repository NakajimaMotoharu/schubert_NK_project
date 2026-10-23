"""Normal six-module fixed-source Main/Test compile, no business/native/Root PT."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='017308824f12515ab5a4450f45d25029954722a5'
SLOT=stage.host.W/'pg7566-backup-health-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7566-backup-health-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
