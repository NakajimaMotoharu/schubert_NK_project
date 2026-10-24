"""Exact52/4, current shared duration encoder and typed SourceKind, one original exec."""
import scoped_prometheus_post as post
import pg8312_timer_encoder_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8312-timer-encoder-host-v1'
    post.RAW_SHA = '75eeb2c810a33d67a27ff358eb7c579db081917e9fb88d2791395d5025d6da75'
    post.SLOT = post.host.W / 'pg8314-timer-encoder-post-v1'
    post.OUT = post.host.BASE / 'PG8314-timer-encoder-post-v1'
    post.MODULE = 'bootstrap'
    post.PREFIX = 'dev/codex/schubert/nk/bootstrap/monitoring/'
    p = post.PREFIX
    post.NAMES = {p + 'PrometheusSummaryExporter', p + 'PrometheusSummaryExporter$SourceKind'}
    post.SOURCE_PATHS = {'src/schubert-nk-bootstrap/src/main/java/' + p + 'PrometheusSummaryExporter.java'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {p + 'PrometheusSummaryExporter$SourceKind': ['values', 'valueOf']}
    post.ENUM_TYPES = set(post.GENERATED)
    post.WITNESS_CASE_PREFIXES = ('timerenc016',)
    post.EXPECTED_SESSION = 'PG8312-TIMER-ENCODER'
    post.main()
