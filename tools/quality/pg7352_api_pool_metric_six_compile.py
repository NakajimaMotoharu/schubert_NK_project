"""Normal six Main/Test compile/package only, not actual pool/DB/collector operations."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='d23758f47c80e1c90baacfe4fade12b968dda2fa'
SLOT=stage.host.W/'pg7352-api-pool-metric-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7352-api-pool-metric-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
