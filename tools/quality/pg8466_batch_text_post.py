"""Independent original Batch text32 and exact one class, no writer or historical qualification."""
import scoped_prometheus_post as post
import pg8464_batch_text_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8464-batch-text-host-v1'
    post.RAW_SHA = 'f6fa626f636469c0ca110289ff1f1b687096a8b12768a0490cafcfbba533207a'
    post.SLOT = post.host.W / 'pg8466-batch-text-post-v1'
    post.OUT = post.host.BASE / 'PG8466-batch-text-post-v1'
    post.MODULE = 'batch'
    post.PREFIX = 'dev/codex/schubert/nk/batch/monitoring/'
    post.NAMES = {post.PREFIX + 'BatchMetricText'}
    post.SOURCE_PATHS = {'src/schubert-nk-batch/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8464-BATCH-TEXT'
    post.main()


