"""Normal six module Main/Test compile/package, no actual transfer/Root/control or executed PT here."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='74371ae0b185cee42e9b6930d68e34522640c2d6'
SLOT=stage.host.W/'pg7290-transfer-health-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7290-transfer-health-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
