"""Normal six compile of observation-clock candidate, all PT unrun here."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='3b2ef576cf46763d67a9e2914dc547afd2f93ef6'
SLOT=stage.host.W/'pg7170-observation-clock-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7170-observation-clock-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
