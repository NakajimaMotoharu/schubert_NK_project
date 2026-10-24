"""Independent original Batch label14 and exact one class, no writer or historical qualification."""
import scoped_prometheus_post as post
import pg8452_batch_label_policy_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8452-batch-label-policy-host-v1'
    post.RAW_SHA = 'a77dfa7b20135cb6eeea8f4ae6d6bd973d6cfe60a3ddade81e9cf2eec3406707'
    post.SLOT = post.host.W / 'pg8454-batch-label-policy-post-v1'
    post.OUT = post.host.BASE / 'PG8454-batch-label-policy-post-v1'
    post.MODULE = 'batch'
    post.PREFIX = 'dev/codex/schubert/nk/batch/monitoring/'
    post.NAMES = {post.PREFIX + 'BatchMetricLabelPolicy'}
    post.SOURCE_PATHS = {'src/schubert-nk-batch/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8452-BATCH-LABEL-POLICY'
    post.main()

