"""Fixed source normal six Main/Test compile/package; business/native tests not invoked."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='d8df90b1e200d970265f90143c1605a6422a6b1e'
SLOT=stage.host.W/'pg7648-mq-pressure-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7648-mq-pressure-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
