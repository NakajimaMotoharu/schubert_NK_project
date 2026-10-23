"""Normal current six-module compile after health input addition; no test or runtime replay."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='bbc230f8a892d3ad2e47aeaccbe37bbb86bd97b6'
SLOT=stage.host.W/'pg7156-filesystem-health-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7156-filesystem-health-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
