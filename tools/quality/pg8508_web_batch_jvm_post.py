"""Original Web/Batch JVM28 and exact two new role classes, no historical API transfer."""
import scoped_prometheus_post as post
import pg8506_web_batch_jvm_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8506-web-batch-jvm-host-v1'
    post.RAW_SHA = '7900277cfec6773889eada0d9c692f0fc4392b66b705a86b53a4cf67685651dc'
    post.SLOT = post.host.W / 'pg8508-web-batch-jvm-post-v1'
    post.OUT = post.host.BASE / 'PG8508-web-batch-jvm-post-v1'
    web = 'dev/codex/schubert/nk/web/monitoring/'
    batch = 'dev/codex/schubert/nk/batch/monitoring/'
    post.MODULE = 'web'
    post.PREFIX = web
    post.NAMES = {web + 'WebJvmMetrics', batch + 'BatchJvmMetrics'}
    post.CLASS_MODULES = {batch + name: 'batch' for name in ('BatchJvmMetrics', 'package-info')}
    post.COMPONENT_METADATA = {batch + 'package-info'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + web + 'WebJvmMetrics.java', 'src/schubert-nk-batch/src/main/java/' + batch + 'BatchJvmMetrics.java'}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8506-WEB-BATCH-JVM'
    post.main()

