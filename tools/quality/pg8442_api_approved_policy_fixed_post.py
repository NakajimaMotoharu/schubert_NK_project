"""Same source original94/7, exact API approved catalog/policy/scalar/Summary four classes."""
import scoped_prometheus_post as post
import pg8440_api_approved_policy_fixed_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8440-api-approved-policy-fixed-host-v1'
    post.RAW_SHA = '217570fb395ff2333cccfce5c21ec192d5e93403afc460521f00415926a7ef5c'
    post.SLOT = post.host.W / 'pg8442-api-approved-policy-fixed-post-v1'
    post.OUT = post.host.BASE / 'PG8442-api-approved-policy-fixed-post-v1'
    post.NAMES = {post.PREFIX + name for name in ('ApiMetricCatalog','ApiMetricScrape','ApiScalarMetricExporter','ApiDurationMetricExporter')}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8440-API-APPROVED-POLICY'
    post.main()


