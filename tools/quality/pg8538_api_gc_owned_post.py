"""Independent exact original API GC14 and one executable class qualification."""
import scoped_prometheus_post as post
import pg8536_api_gc_owned_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8536-api-gc-owned-host-v1'
    post.RAW_SHA = '989bc7adc9ddb94fddb773986e9426e161fc1c365ef5af55f1596ee983c18a50'
    post.SLOT = post.host.W / 'pg8538-api-gc-owned-post-v1'
    post.OUT = post.host.BASE / 'PG8538-api-gc-owned-post-v1'
    post.NAMES = {post.PREFIX + 'ApiGcMetricRegistration'}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8536-API-GC'
    post.main()
