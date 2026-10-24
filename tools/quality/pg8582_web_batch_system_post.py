"""Original Web/Batch JVM28 and exact two new role classes, no historical API transfer."""
import scoped_prometheus_post as post
import pg8580_web_batch_system_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8580-web-batch-system-host-v1'
    post.RAW_SHA = '9da560ee842895892fe780274977691e30548f420473edc8d04aeb393f6a4be1'
    post.SLOT = post.host.W / 'pg8582-web-batch-system-post-v1'
    post.OUT = post.host.BASE / 'PG8582-web-batch-system-post-v1'
    web = 'dev/codex/schubert/nk/web/monitoring/'
    batch = 'dev/codex/schubert/nk/batch/monitoring/'
    post.MODULE = 'web'
    post.PREFIX = web
    post.NAMES = {web + 'WebSystemMetrics', batch + 'BatchSystemMetrics'}
    post.CLASS_MODULES = {batch + name: 'batch' for name in ('BatchSystemMetrics', 'package-info')}
    post.COMPONENT_METADATA = {batch + 'package-info'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + web + 'WebSystemMetrics.java', 'src/schubert-nk-batch/src/main/java/' + batch + 'BatchSystemMetrics.java'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8580-WEB-BATCH-SYSTEM'
    post.main()
