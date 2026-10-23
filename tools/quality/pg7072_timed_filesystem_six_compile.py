"""First six-module package of the fixed70 source; tests explicitly not executed."""
import pg7030_monitoring_six_compile as stage

SOURCE='d96df9f09b46dee9aa75276d474e118609ee890c'
SLOT=stage.host.W/'pg7072-timed-filesystem-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE
    stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7072-timed-filesystem-six-compile-v1'
    stage.main()
