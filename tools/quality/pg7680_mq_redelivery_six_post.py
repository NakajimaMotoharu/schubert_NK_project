"""Parameterized exact existing six-Jar validator; current API122/25 and historical owners separate."""
import pg7664_mq_pressure_six_post_v2 as audit
import pg7678_mq_redelivery_six_compile as compilation

if __name__=='__main__':
    audit.compilation=compilation
    audit.SLOT=audit.host.W/'pg7680-mq-redelivery-six-post-v1'
    audit.OUT=audit.host.BASE/'PG7680-mq-redelivery-six-post-v1'
    audit.CURRENT_TESTS=122;audit.CURRENT_SUITES=15;audit.CURRENT_PHYSICAL=25
    audit.PHYSICAL_COUNT=1764;audit.SOURCE_DELTA_COUNT=108
    audit.PINS=dict(audit.PINS)
    path='PG7676-mq-redelivery-post-v1/manifest.json'
    audit.PINS['currentApi']=(path,audit.host.sha(audit.host.BASE/path))
    audit.main()
