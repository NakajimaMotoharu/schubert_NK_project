"""First normal six-module package of actual Micrometer recorder15 source, no tests invoked."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='ef6f9f22aaa8b16ffcfe39952bfc9a2196b0308a'
SLOT=stage.host.W/'pg7120-micrometer-http-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE
    stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7120-micrometer-http-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
