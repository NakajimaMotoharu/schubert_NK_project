"""Original14/1 and exact new stateless Web mode policy class, no old counters transferred."""
import scoped_prometheus_post as post
import pg8408_web_scrape_host as original

if __name__ == '__main__':
    post.common.SOURCE = original.SOURCE
    post.common.COMPILE = original.COMPILE
    post.common.COMPILE_SHA = original.COMPILE_SHA
    post.RUN = post.host.W / 'pg8408-web-scrape-host-v1'
    post.RAW_SHA = '38d2762a224f340409127e3488226b3c90fd49520ee3d9dae3d5a8111cdb8fc7'
    post.SLOT = post.host.W / 'pg8410-web-scrape-post-v1'
    post.OUT = post.host.BASE / 'PG8410-web-scrape-post-v1'
    post.MODULE = 'web'
    post.PREFIX = 'dev/codex/schubert/nk/web/monitoring/'
    post.NAMES = {post.PREFIX + 'WebMetricScrape'}
    post.SOURCE_PATHS = {'src/schubert-nk-web/src/main/java/' + name + '.java' for name in post.NAMES}
    post.COUNTS = original.COUNTS
    post.GENERATED = {}
    post.ENUM_TYPES = set()
    post.WITNESS_CASE_PREFIXES = ()
    post.EXPECTED_SESSION = 'PG8408-WEB-SCRAPE'
    post.main()
