"""Normal six Main/Test compilation first; no actual service/HTTP/stream/native execution."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='a1b5285474ebbc926091fd2ce7a279367878338f'
SLOT=stage.host.W/'pg7730-media-stream-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7730-media-stream-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
