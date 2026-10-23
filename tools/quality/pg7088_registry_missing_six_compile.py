"""First six-module package of registry-missing73 source; PT explicitly unrun."""
import pg7030_monitoring_six_compile as stage

SOURCE='71c6be37c1a0038314b66565b1188d6488bc7c8d'
SLOT=stage.host.W/'pg7088-registry-missing-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE
    stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7088-registry-missing-six-compile-v1'
    stage.main()
