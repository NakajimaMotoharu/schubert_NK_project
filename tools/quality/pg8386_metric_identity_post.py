"""Original100/9 and current API/Web five classes, one exec and no source/coverage union."""
import scoped_prometheus_post as post
import pg8384_metric_identity_full_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8384-metric-identity-full-host-v1'
    post.RAW_SHA = '2520ca00c89cfa91866cea441d22a866173a03578f323eb1d156eccf99424ecc'
    post.SLOT = post.host.W / 'pg8386-metric-identity-post-v1'
    post.OUT = post.host.BASE / 'PG8386-metric-identity-post-v1'
    api = 'dev/codex/schubert/nk/api/monitoring/'
    web = 'dev/codex/schubert/nk/web/monitoring/'
    post.PREFIX = api
    web_names = ('WebCounterMetricExporter', 'WebGaugeMetricExporter', 'WebDurationMetricExporter', 'WebMetricText')
    post.NAMES = {api + 'ApiDurationMetricExporter', *[web + name for name in web_names]}
    post.CLASS_MODULES = {web + name: 'web' for name in (*web_names, 'package-info')}
    post.COMPONENT_METADATA = {web + 'package-info'}
    post.SOURCE_PATHS = {
        'src/schubert-nk-api/src/main/java/' + api + 'ApiDurationMetricExporter.java',
        *['src/schubert-nk-web/src/main/java/' + web + name + '.java' for name in web_names]}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8384-METRIC-IDENTITY'
    post.EXPECTED_FIXTURE_HASHES = {
        str(post.host.ROOT / original.FIXTURE): original.FIXTURE_SHA,
        str(post.RUN / 'fresh-test-classes/monitoring/http-route-labels.txt'): original.FIXTURE_SHA}
    post.main()
