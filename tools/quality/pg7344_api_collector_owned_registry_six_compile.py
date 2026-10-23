"""BUG1659 fixed-source normal six Main/Test compile/package only, no actual DB operations."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk

SOURCE='003adea1e2d77b853be874fef26d17b50e2abbbc'
SLOT=stage.host.W/'pg7344-api-collector-owned-registry-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE;stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7344-api-collector-owned-registry-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.main()
