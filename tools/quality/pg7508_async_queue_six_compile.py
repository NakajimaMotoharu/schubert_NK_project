"""Fixed source normal six Main/Test compile/package only, not actual queue/DB/native PT."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='d56b2cc0a655e75174b5e2e8871abf5bd3d3b15d'
SLOT=stage.host.W/'pg7508-async-queue-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7508-async-queue-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
