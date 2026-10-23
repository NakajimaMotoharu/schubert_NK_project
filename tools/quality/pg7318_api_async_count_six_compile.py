"""Normal six-module compile/package only; JDBC doubles do not authorize actual DB startup."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='faf7b0756d5a4fbb4098c17c2667ee7cf54b585c'
SLOT=stage.host.W/'pg7318-api-async-count-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7318-api-async-count-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
