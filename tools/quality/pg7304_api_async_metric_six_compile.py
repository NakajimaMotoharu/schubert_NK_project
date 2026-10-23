"""Normal six module Main/Test compile/package, API metrics are not actual API/DB/Root startup."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='72b65394206ac449604e4cffc5d703c55d8fc2f7'
SLOT=stage.host.W/'pg7304-api-async-metric-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7304-api-async-metric-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
