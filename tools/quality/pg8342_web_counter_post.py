"""One original44/4 exec and exact current Web three classes, no historical coverage union."""
import scoped_prometheus_post as post
import pg8340_web_counter_fixed_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8340-web-counter-fixed-host-v1'
    post.RAW_SHA = 'a1e50085164df45a20b1bf88585d4642a58a14641187c930a0bb0d4f42016756'
    post.SLOT = post.host.W / 'pg8342-web-counter-post-v1'
    post.OUT = post.host.BASE / 'PG8342-web-counter-post-v1'
    post.MODULE = 'web'
    post.PREFIX = 'dev/codex/schubert/nk/web/monitoring/'
    post.NAMES = {post.PREFIX + name for name in ('WebCounterMetricExporter', 'WebDurationMetricExporter', 'WebMetricText')}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8340-WEB-COUNTER'
    post.EXPECTED_FIXTURE_HASHES = {
        str(post.host.ROOT / original.FIXTURE): original.FIXTURE_SHA,
        str(post.RUN / 'fresh-test-classes/monitoring/http-route-labels.txt'): original.FIXTURE_SHA}
    post.main()
