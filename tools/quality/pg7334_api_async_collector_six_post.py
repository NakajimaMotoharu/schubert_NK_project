"""Current API24 vs separate historical byte-only Batch/Web domains."""
import pg7306_api_async_metric_six_post as post
import pg7344_api_collector_owned_registry_six_compile as compilation

if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7334-api-async-collector-six-post-v1'
    post.OUT=post.host.BASE/'PG7334-api-async-collector-six-post-v1'
    post.PINS=dict(post.PINS)
    path='PG7342-api-collector-owned-registry-post-v1/manifest.json'
    post.PINS['currentApi']=(path,post.host.sha(post.host.BASE/path))
    post.CURRENT_TESTS=24;post.CURRENT_SUITES=3;post.CURRENT_PHYSICAL=6
    post.PHYSICAL_COUNT=1728;post.SOURCE_DELTA_COUNT=69
    post.main()
