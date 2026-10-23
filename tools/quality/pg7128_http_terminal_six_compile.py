"""Normal six-source compile and Maven-resolved test classpaths; no tests or target operations."""
import pg7030_monitoring_six_compile as stage
import pg7106_micrometer_http_host as sdk


if __name__=='__main__':
    import subprocess
    stage.SOURCE=subprocess.check_output(['git','rev-parse','HEAD'],cwd=stage.host.ROOT,text=True).strip()
    stage.SLOT=stage.host.W/'pg7128-http-terminal-six-compile-v1'
    stage.OUT=stage.host.BASE/'PG7128-http-terminal-six-compile-v1'
    stage.DEPENDENCY_JARS=sdk.SDK
    stage.CAPTURE_TEST_CLASSPATH=True
    stage.main()
