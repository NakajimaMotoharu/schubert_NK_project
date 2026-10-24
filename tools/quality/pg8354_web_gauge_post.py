"""Current new Gauge plus unchanged Web-local text helper, original22/2 one exec only."""
import scoped_prometheus_post as post
import pg8352_web_gauge_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8352-web-gauge-host-v1'
    post.RAW_SHA = '7993a17f762e2efd3483378ae7e508c0dddf05c8acbf1b528803c47f56a12d8b'
    post.SLOT = post.host.W / 'pg8354-web-gauge-post-v1'
    post.OUT = post.host.BASE / 'PG8354-web-gauge-post-v1'
    post.MODULE = 'web'
    post.PREFIX = 'dev/codex/schubert/nk/web/monitoring/'
    post.NAMES = {post.PREFIX + name for name in ('WebGaugeMetricExporter', 'WebMetricText')}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8352-WEB-GAUGE'
    post.main()
