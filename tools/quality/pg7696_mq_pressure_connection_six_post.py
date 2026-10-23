"""Exact normal six validator reused with fixed current API130/26 and all1765 physical bytes."""
import pg7664_mq_pressure_six_post_v2 as audit
import pg7694_mq_pressure_connection_six_compile as compilation

if __name__=='__main__':
    audit.compilation=compilation
    audit.SLOT=audit.host.W/'pg7696-mq-pressure-connection-six-post-v1'
    audit.OUT=audit.host.BASE/'PG7696-mq-pressure-connection-six-post-v1'
    audit.CURRENT_TESTS=130;audit.CURRENT_SUITES=16;audit.CURRENT_PHYSICAL=26
    audit.PHYSICAL_COUNT=1765;audit.SOURCE_DELTA_COUNT=110
    audit.PINS=dict(audit.PINS)
    path='PG7692-mq-pressure-connection-post-v1/manifest.json'
    audit.PINS['currentApi']=(path,audit.host.sha(audit.host.BASE/path))
    audit.main()
