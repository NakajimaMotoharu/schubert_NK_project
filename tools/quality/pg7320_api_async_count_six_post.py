"""Current API16 vs historical Batch/Web bytes, not cross-source execution/coverage."""
import pg7306_api_async_metric_six_post as post
import pg7318_api_async_count_six_compile as compilation

if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7320-api-async-count-six-post-v1'
    post.OUT=post.host.BASE/'PG7320-api-async-count-six-post-v1'
    post.PINS=dict(post.PINS)
    path='PG7316-api-async-count-post-v1/manifest.json'
    post.PINS['currentApi']=(path,post.host.sha(post.host.BASE/path))
    post.CURRENT_TESTS=16;post.CURRENT_SUITES=2;post.CURRENT_PHYSICAL=5
    post.PHYSICAL_COUNT=1727;post.SOURCE_DELTA_COUNT=67
    post.main()
