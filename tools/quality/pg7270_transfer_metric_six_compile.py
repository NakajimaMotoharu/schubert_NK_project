"""Normal six module Main/Test compile/package, no actual files or executed PT here."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='936c727ea50906c64520b607cc9e93b6fd584544'
SLOT=stage.host.W/'pg7270-transfer-metric-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7270-transfer-metric-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
