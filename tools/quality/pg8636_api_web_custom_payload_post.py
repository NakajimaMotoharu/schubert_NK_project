"""Original26 and exact two pure role-local payload classes; no endpoint/Root invocation."""
import scoped_prometheus_post as post
import pg8634_api_web_custom_payload_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8634-api-web-custom-payload-host-v1'
    post.RAW_SHA = '5f09c33d46e0a3a9de6ab0259a0fd4c110e2aff7c95570f9cc6ed4cfebbeafac'
    post.SLOT = post.host.W / 'pg8636-api-web-custom-payload-post-v1'
    post.OUT = post.host.BASE / 'PG8636-api-web-custom-payload-post-v1'
    api = 'dev/codex/schubert/nk/api/monitoring/'
    web = 'dev/codex/schubert/nk/web/monitoring/'
    post.MODULE = 'web'
    post.PREFIX = web
    post.NAMES = {api + 'ApiCustomMetricPayload', web + 'WebCustomMetricPayload'}
    post.CLASS_MODULES = {api + name: 'api' for name in ('ApiCustomMetricPayload', 'package-info')}
    post.COMPONENT_METADATA = {api + 'package-info'}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + api + 'ApiCustomMetricPayload.java', 'src/schubert-nk-web/src/main/java/' + web + 'WebCustomMetricPayload.java'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8634-API-WEB-CUSTOM'
    post.main()
