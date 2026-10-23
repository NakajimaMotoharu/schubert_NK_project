"""Current API56/exact old physical domains; current auxiliary inputs separately pinned."""
import pg7306_api_async_metric_six_post as post
import pg7380_api_operation_mismatch_six_compile as compilation
import pg7362_api_pool_observation_host as host

if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7382-api-operation-mismatch-six-post-v1'
    post.OUT=post.host.BASE/'PG7382-api-operation-mismatch-six-post-v1'
    post.PINS=dict(post.PINS)
    path='PG7378-api-operation-mismatch-post-v1/manifest.json'
    post.PINS['currentApi']=(path,post.host.sha(post.host.BASE/path))
    post.CURRENT_TESTS=56;post.CURRENT_SUITES=7;post.CURRENT_PHYSICAL=13
    post.PHYSICAL_COUNT=1735;post.SOURCE_DELTA_COUNT=77
    post.EXTRA_CURRENT_AUXILIARY_JARS=host.EXTRA
    post.main()
