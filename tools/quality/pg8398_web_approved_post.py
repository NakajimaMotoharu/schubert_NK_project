"""Original96/9 approved point join, exact Web five classes, no historical coverage union."""
import scoped_prometheus_post as post
import pg8396_web_approved_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8396-web-approved-host-v1'
    post.RAW_SHA = '0b1cd4286b16863f755cdce920f67c84ae1ac610954ea1a3f17dd250755c9623'
    post.SLOT = post.host.W / 'pg8398-web-approved-post-v1'
    post.OUT = post.host.BASE / 'PG8398-web-approved-post-v1'
    post.MODULE = 'web'
    post.PREFIX = 'dev/codex/schubert/nk/web/monitoring/'
    names = ('WebCounterMetricExporter', 'WebGaugeMetricExporter', 'WebDurationMetricExporter', 'WebMetricCatalog', 'WebMetricText')
    post.NAMES = {post.PREFIX + name for name in names}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8396-WEB-APPROVED'
    post.EXPECTED_FIXTURE_HASHES = {
        str(post.host.ROOT / original.FIXTURE): original.FIXTURE_SHA,
        str(post.RUN / 'fresh-test-classes/monitoring/http-route-labels.txt'): original.FIXTURE_SHA}
    post.main()
