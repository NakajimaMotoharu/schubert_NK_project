"""Fixed private names, normal six module Main/Test compile/package, PT unrun here."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='1470b0ea110bcf9598bcdc423745b812b580f9ad'
SLOT=stage.host.W/'pg7276-transfer-metric-six-compile-v2'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7276-transfer-metric-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
