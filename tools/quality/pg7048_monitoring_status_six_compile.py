"""Compile exact qualified54 source, no PT or runtime invocation."""
import pg7030_monitoring_six_compile as stage

SOURCE = '6ebb81e1173e001a627374b533b34766b44785b0'
SLOT = stage.host.W/'pg7048-monitoring-status-six-compile-v1'


if __name__ == '__main__':
    stage.SOURCE = SOURCE
    stage.SLOT = SLOT
    stage.OUT = stage.host.BASE/'PG7048-monitoring-status-six-compile-v1'
    stage.main()
