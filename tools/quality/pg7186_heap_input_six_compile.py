"""Current heap observation source, normal six compile/package only; no actual provider operation."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='dc46262abceaac42085a813d872f25669700a096'
SLOT=stage.host.W/'pg7186-heap-input-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7186-heap-input-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
