"""Independent exact original API GC14 and one executable class qualification."""
import scoped_prometheus_post as post
import pg8592_api_standard_assembly_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8592-api-standard-assembly-host-v1'
    post.RAW_SHA = '2b75cd3c64cf84795540fffc0e6d419e25725988e70cc4f19f1db363773cac68'
    post.SLOT = post.host.W / 'pg8600-api-standard-assembly-post-v1'
    post.OUT = post.host.BASE / 'PG8600-api-standard-assembly-post-v1'
    post.NAMES = {post.PREFIX + 'ApiStandardMetrics'}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8592-API-STANDARD'
    post.main()
