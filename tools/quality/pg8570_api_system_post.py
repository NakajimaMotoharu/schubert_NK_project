"""Independent exact original API GC14 and one executable class qualification."""
import scoped_prometheus_post as post
import pg8568_api_system_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8568-api-system-host-v1'
    post.RAW_SHA = 'f62c2bb691831359074a2d4fffea8f58a86ac1bfcc0a40671bf4c6ffe13be6ef'
    post.SLOT = post.host.W / 'pg8570-api-system-post-v1'
    post.OUT = post.host.BASE / 'PG8570-api-system-post-v1'
    post.NAMES = {post.PREFIX + 'ApiSystemMetrics'}
    post.SOURCE_PATHS = {'src/schubert-nk-api/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8568-API-SYSTEM'
    post.main()
