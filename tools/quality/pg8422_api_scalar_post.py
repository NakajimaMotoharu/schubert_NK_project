"""Independent original32/2 exact API scalar class counters/static, no old coverage transfer."""
import scoped_prometheus_post as post
import pg8420_api_scalar_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8420-api-scalar-host-v1'
    post.RAW_SHA = 'ddf1af1d14ea273f873a5f46ab4c202ac7c1cd4802a0002f4bdc4f23ed001557'
    post.SLOT = post.host.W / 'pg8422-api-scalar-post-v1'
    post.OUT = post.host.BASE / 'PG8422-api-scalar-post-v1'
    post.NAMES = {post.PREFIX + 'ApiScalarMetricExporter'}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8420-API-SCALAR'
    post.main()

