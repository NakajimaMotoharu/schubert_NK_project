"""Fresh Test-only source normal compile/test-classpath capture; PT0 explicitly unrun."""
import subprocess
import pg7030_monitoring_six_compile as stage
import pg7362_api_pool_observation_host as sdk

SOURCE=None
SLOT=stage.host.W/'pg7440-web-generated-six-compile-v1'

if __name__=='__main__':
    stage.SOURCE=subprocess.check_output(['git','rev-parse','HEAD'],cwd=stage.host.ROOT,text=True).strip()
    stage.SLOT=SLOT;stage.OUT=stage.host.BASE/'PG7440-web-generated-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.DEPENDENCIES;stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()
