"""Same source original94/7, exact API approved catalog/policy/scalar/Summary four classes."""
import scoped_prometheus_post as post
import pg8432_api_approved_policy_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8432-api-approved-policy-host-v1'
    post.RAW_SHA = '3ef9e95a693b9085b39e4bf61ed0bd6e563f78c718b0a02d3aa6dde8cb9e996a'
    post.SLOT = post.host.W / 'pg8434-api-approved-policy-post-v1'
    post.OUT = post.host.BASE / 'PG8434-api-approved-policy-post-v1'
    post.NAMES = {post.PREFIX + name for name in ('ApiMetricCatalog','ApiMetricScrape','ApiScalarMetricExporter','ApiDurationMetricExporter')}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8432-API-APPROVED-POLICY'
    post.main()

