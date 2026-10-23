"""Owner failure visibility corrected source, normal six compile, old actual23 kept as history."""
import subprocess
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk


if __name__=='__main__':
    stage.SOURCE=subprocess.check_output(['git','rev-parse','HEAD'],cwd=stage.host.ROOT,text=True).strip()
    stage.SLOT=stage.host.W/'pg7136-http-terminal-six-compile-v3'
    stage.OUT=stage.host.BASE/'PG7136-http-terminal-six-compile-v3'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()
