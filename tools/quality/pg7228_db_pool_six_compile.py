"""Normal six module Main/Test compile/package, not executed PT."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='e9c0ba2a180262f8410ae16c46f5909787b5132b'
SLOT=stage.host.W/'pg7228-db-pool-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7228-db-pool-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
