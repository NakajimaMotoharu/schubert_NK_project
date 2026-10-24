"""Original corrected API JVM14 and exact new class, no old failed counter transfer."""
import scoped_prometheus_post as post
import pg8494_api_jvm_oracle_fixed_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8494-api-jvm-oracle-fixed-host-v1'
    post.RAW_SHA = 'aaabb5abc69157fcccb592a663609435009b4b1a53c5fd5024cc7b28dae20d1a'
    post.SLOT = post.host.W / 'pg8496-api-jvm-post-v1'
    post.OUT = post.host.BASE / 'PG8496-api-jvm-post-v1'
    post.NAMES = {post.PREFIX + 'ApiJvmMetrics'}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8494-API-JVM'
    post.main()

