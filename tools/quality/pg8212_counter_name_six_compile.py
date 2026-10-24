"""New BUG1691 fixed-source normal six compile/NullAway/classpath, PT0/UNRUN."""
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE='6246c954d6d0ac7171bf009663bb2e6539d8be32'
SLOT=stage.host.W/'pg8212-counter-name-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=SOURCE
    stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG8212-counter-name-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES
    stage.main()
