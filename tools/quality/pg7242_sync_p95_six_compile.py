"""Normal six module Main/Test compile/package, PT remains unrun here."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='00edd88adbff2625fdd479224e0d3a12bd188861'
SLOT=stage.host.W/'pg7242-sync-p95-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7242-sync-p95-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
