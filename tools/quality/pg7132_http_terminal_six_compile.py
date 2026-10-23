"""Corrected fixture's normal six compile; keeps failed7128 intact, no test or target operations."""
import subprocess
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk


if __name__=='__main__':
    stage.SOURCE=subprocess.check_output(['git','rev-parse','HEAD'],cwd=stage.host.ROOT,text=True).strip()
    stage.SLOT=stage.host.W/'pg7132-http-terminal-six-compile-v2'
    stage.OUT=stage.host.BASE/'PG7132-http-terminal-six-compile-v2'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()
