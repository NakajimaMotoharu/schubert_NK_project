"""Independent164/20 current34 exact XML/CRC/counter/static verification, no Root operation."""
import pg7914_mq_event_post as previous
import pg7962_duration_extreme_host as host
METHODS={'dbTime009ExtremeRangeOrdersKeepIndependentSmallBucketCountsAndFiniteTotals',
 'mqTime009ExtremeRangeOrdersKeepIndependentSmallBucketCountsAndFiniteTotals'}
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7962-duration-extreme-host-v1'
    post.OUT=post.host.BASE/'PG7964-duration-extreme-post-v1'
    post.PRIVATE=post.host.W/'pg7964-duration-extreme-post-v1'
    post.METHODS|=METHODS
    for name in ('DbQueryDurationMetricRecorderTest','MqProcessingDurationMetricRecorderTest'):
        post.EXPECTED_SUITES['dev.codex.schubert.nk.api.monitoring.'+name]=dict(tests=9,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=164
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
