"""Independent exact original API GC14 and one executable class qualification."""
import scoped_prometheus_post as post
import pg8526_api_gc_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8526-api-gc-host-v1'
    post.RAW_SHA = '274a4517544977abb67212dd0294dd6c951aa141343d4af42003e2e64959680b'
    post.SLOT = post.host.W / 'pg8528-api-gc-post-v1'
    post.OUT = post.host.BASE / 'PG8528-api-gc-post-v1'
    post.NAMES = {post.PREFIX + 'ApiGcMetricRegistration'}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8526-API-GC'
    post.main()
