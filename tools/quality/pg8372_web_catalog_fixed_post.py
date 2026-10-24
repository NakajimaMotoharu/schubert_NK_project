"""Original14/1 exact new Web catalog class, one actual exec/CRC, no old coverage union."""
import scoped_prometheus_post as post
import pg8370_web_catalog_fixed_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8370-web-catalog-fixed-host-v1'
    post.RAW_SHA = '4024e0c17c2fc7993c69bff14b536fbed73fd0c0e16b04f304581fc149d2b729'
    post.SLOT = post.host.W / 'pg8372-web-catalog-fixed-post-v1'
    post.OUT = post.host.BASE / 'PG8372-web-catalog-fixed-post-v1'
    post.MODULE = 'web'
    post.PREFIX = 'dev/codex/schubert/nk/web/monitoring/'
    post.NAMES = {post.PREFIX + 'WebMetricCatalog'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8370-WEB-CATALOG'
    post.EXPECTED_FIXTURE_HASHES = {
        str(post.host.ROOT / original.FIXTURE): original.FIXTURE_SHA,
        str(post.RUN / 'fresh-test-classes/monitoring/http-route-labels.txt'): original.FIXTURE_SHA}
    post.main()
