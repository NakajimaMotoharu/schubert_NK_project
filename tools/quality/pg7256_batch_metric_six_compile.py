"""Normal six module Main/Test compile/package, no actual Batch or executed PT here."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='34813cef90b2a5c6b2ad3be835565bf53e96a875'
SLOT=stage.host.W/'pg7256-batch-metric-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7256-batch-metric-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
