"""Normal six-module Main/Test compile/package only, no actual collector/DB/Root startup."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='d791e5c8dc940aea673da42032b11a4d6ee55b8e'
SLOT=stage.host.W/'pg7332-api-async-collector-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7332-api-async-collector-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
