"""Original Web/Batch JVM28 and exact two new role classes, no historical API transfer."""
import scoped_prometheus_post as post
import pg8610_web_batch_standard_assembly_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8610-web-batch-standard-assembly-host-v1'
    post.RAW_SHA = 'fd22dd1aa7e1b7a0867670e41ee7d4f9fce295f87291351885b229b676963124'
    post.SLOT = post.host.W / 'pg8612-web-batch-standard-assembly-post-v1'
    post.OUT = post.host.BASE / 'PG8612-web-batch-standard-assembly-post-v1'
    web = 'dev/codex/schubert/nk/web/monitoring/'
    batch = 'dev/codex/schubert/nk/batch/monitoring/'
    post.MODULE = 'web'
    post.PREFIX = web
    post.NAMES = {web + 'WebStandardMetrics', batch + 'BatchStandardMetrics'}
    post.CLASS_MODULES = {batch + name: 'batch' for name in ('BatchStandardMetrics', 'package-info')}
    post.COMPONENT_METADATA = {batch + 'package-info'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + web + 'WebStandardMetrics.java', 'src/schubert-nk-batch/src/main/java/' + batch + 'BatchStandardMetrics.java'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8610-WEB-BATCH-STANDARD'
    post.main()
