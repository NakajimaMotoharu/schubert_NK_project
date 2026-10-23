"""First six-module package of HTTP label source; no PT/DB/native invocation."""
import pg7030_monitoring_six_compile as stage

SOURCE='76f931d2a219ddee619022bca6fc6c27f59abd81'
SLOT=stage.host.W/'pg7100-web-http-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE
    stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7100-web-http-six-compile-v1'
    stage.main()
