"""Current108/Batch27 physical vs historical Web10, no current-source coverage synthesis."""
import pg7158_filesystem_health_six_post as post
import pg7200_timed_heap_six_compile as compilation


if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7202-timed-heap-six-post-v1'
    post.OUT=post.host.BASE/'PG7202-timed-heap-six-post-v1'
    post.PINS['currentBatch']=('PG7198-timed-heap-post-v1/manifest.json',
                              'e0186e220a22556c0706b55513f287924e6326bd75699fd19a5bca85cfa0a6be')
    post.CURRENT_TESTS=108;post.CURRENT_SUITES=15;post.CURRENT_PHYSICAL=27
    post.PHYSICAL_COUNT=1706;post.SOURCE_DELTA_COUNT=44
    post.main()
