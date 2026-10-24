"""Current32/4 original exec, two repaired classfiles, exact fixture and empty marker proof."""
import scoped_prometheus_post as post
import pg8298_http_cdf_fixed_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8298-http-cdf-fixed-host-v1'
    post.RAW_SHA = 'e69c0ed6965ce7bab662778764182f9bac747b957541cb2d2b74d40576a982b9'
    post.SLOT = post.host.W / 'pg8300-http-cdf-fixed-post-v1'
    post.OUT = post.host.BASE / 'PG8300-http-cdf-fixed-post-v1'
    post.MODULE = 'web'
    post.PREFIX = 'dev/codex/schubert/nk/web/monitoring/'
    p = post.PREFIX
    post.NAMES = {p + 'OverflowSafeHttpMeterRegistry', p + 'OverflowSafeHttpMeterRegistry$OverflowSafeTimer'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + p + 'OverflowSafeHttpMeterRegistry.java'}
    post.MARKERS = {p + 'OverflowSafeDurationSupport': 'Empty package-local capability marker; prove fields/methods/initializers zero, never omit executable code.'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8298-HTTP-CDF-FIXED'
    post.EXPECTED_FIXTURE_HASHES = {
        str(post.host.ROOT / original.FIXTURE): original.FIXTURE_SHA,
        str(post.RUN / 'fresh-test-classes/monitoring/http-route-labels.txt'): original.FIXTURE_SHA}
    post.main()
