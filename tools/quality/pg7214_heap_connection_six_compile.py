"""Normal six Main/Test compile; no executed PT claimed by compilation."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='0b8aa6dab9b91d378811b0bda24d6a61bbc73106'
SLOT=stage.host.W/'pg7214-heap-connection-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7214-heap-connection-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
