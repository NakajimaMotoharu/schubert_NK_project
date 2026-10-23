"""Current protected-alert fix normal six compile/package; no business/Root/native test run."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='9c087705cb88979a947e8ffacbfff0722c736d32'
SLOT=stage.host.W/'pg7552-protected-alert-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7552-protected-alert-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
