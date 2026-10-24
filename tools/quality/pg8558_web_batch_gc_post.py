"""Original Web/Batch JVM28 and exact two new role classes, no historical API transfer."""
import scoped_prometheus_post as post
import pg8556_web_batch_gc_fixed_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8556-web-batch-gc-fixed-host-v1'
    post.RAW_SHA = '2c7aa21cdb9dc434e6b03d3a61f590d6364dd678e77b376e6542e88232a8f174'
    post.SLOT = post.host.W / 'pg8558-web-batch-gc-post-v1'
    post.OUT = post.host.BASE / 'PG8558-web-batch-gc-post-v1'
    web = 'dev/codex/schubert/nk/web/monitoring/'
    batch = 'dev/codex/schubert/nk/batch/monitoring/'
    post.MODULE = 'web'
    post.PREFIX = web
    post.NAMES = {web + 'WebGcMetricRegistration', batch + 'BatchGcMetricRegistration'}
    post.CLASS_MODULES = {batch + name: 'batch' for name in ('BatchGcMetricRegistration', 'package-info')}
    post.COMPONENT_METADATA = {batch + 'package-info'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + web + 'WebGcMetricRegistration.java', 'src/schubert-nk-batch/src/main/java/' + batch + 'BatchGcMetricRegistration.java'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8556-WEB-BATCH-GC'
    post.main()
