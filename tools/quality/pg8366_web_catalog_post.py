"""Original14/1 exact new Web catalog class, one actual exec/CRC, no old coverage union."""
import scoped_prometheus_post as post
import pg8364_web_catalog_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8364-web-catalog-host-v1'
    post.RAW_SHA = '56f70b238d9cb4971281bea0809a1ad932930f023891dc62db8dd77b274e2ef3'
    post.SLOT = post.host.W / 'pg8366-web-catalog-post-v1'
    post.OUT = post.host.BASE / 'PG8366-web-catalog-post-v1'
    post.MODULE = 'web'
    post.PREFIX = 'dev/codex/schubert/nk/web/monitoring/'
    post.NAMES = {post.PREFIX + 'WebMetricCatalog'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8364-WEB-CATALOG'
    post.EXPECTED_FIXTURE_HASHES = {
        str(post.host.ROOT / original.FIXTURE): original.FIXTURE_SHA,
        str(post.RUN / 'fresh-test-classes/monitoring/http-route-labels.txt'): original.FIXTURE_SHA}
    post.main()
