"""Current app-owned API/Web duration adapters, exact52/4 and one original exec."""
import scoped_prometheus_post as post
import pg8322_app_duration_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8322-app-duration-host-v1'
    post.RAW_SHA = 'f6ef95b48d42d8dc8b6dde807ef4bf020fc23c4d294d16a8ab281708ed44b875'
    post.SLOT = post.host.W / 'pg8324-app-duration-post-v1'
    post.OUT = post.host.BASE / 'PG8324-app-duration-post-v1'
    api = 'dev/codex/schubert/nk/api/monitoring/'
    web = 'dev/codex/schubert/nk/web/monitoring/'
    post.PREFIX = api
    post.NAMES = {api + 'ApiDurationMetricExporter', web + 'WebDurationMetricExporter'}
    post.CLASS_MODULES = {web + name: 'web' for name in ('WebDurationMetricExporter', 'package-info')}
    post.COMPONENT_METADATA = {web + 'package-info'}
    post.SOURCE_PATHS = {
        'src/schubert-nk-api/src/main/java/' + api + 'ApiDurationMetricExporter.java',
        'src/schubert-nk-web/src/main/java/' + web + 'WebDurationMetricExporter.java'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8322-APP-DURATION'
    post.main()
