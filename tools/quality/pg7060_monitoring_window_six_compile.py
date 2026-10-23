"""Compile exact qualified62 source; no PT or live runtime operations."""
import pg7030_monitoring_six_compile as stage

SOURCE='bc827c43621961950acd61a2554dca3004493acc'
SLOT=stage.host.W/'pg7060-monitoring-window-six-compile-v1'


if __name__=='__main__':
    stage.SOURCE=SOURCE
    stage.SLOT=SLOT
    stage.OUT=stage.host.BASE/'PG7060-monitoring-window-six-compile-v1'
    stage.main()
