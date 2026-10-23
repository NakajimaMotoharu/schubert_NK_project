"""Normal six compile/package of pure timed heap kernel source; PT stays unrun here."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='41905e2f089eec0aeea8c8f0acca9cc657814a00'
SLOT=stage.host.W/'pg7200-timed-heap-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7200-timed-heap-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
