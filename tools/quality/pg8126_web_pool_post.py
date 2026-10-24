"""Independent actual114/14/all25 plus2 metadata, exact runtime Hikari pins and raw static."""
import pg8062_http_duration_safe_post as post
import pg8124_web_pool_host as original
import pg7362_api_pool_observation_host as libraries
if __name__=='__main__':
    post.original=original
    post.SLOT=post.host.W/'pg8126-web-pool-post-v1';post.OUT=post.host.BASE/'PG8126-web-pool-post-v1'
    post.TOTAL_TESTS=114;post.SUITE_COUNT=14;post.SOURCE_FILE_COUNT=29
    post.NAMES|={post.PREFIX+'WebDbPoolMetricRecorder'+suffix for suffix in ('','$State','$Counts')}
    post.NAMES|={post.PREFIX+'WebDbPoolMetricObservation',post.PREFIX+'WebDbPoolMetricCollector'}
    post.EXTRA_TYPED_POOL_JARS=libraries.EXTRA
    post.main()
