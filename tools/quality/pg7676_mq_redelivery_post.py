"""Independent same-source122/15, exact24 executables/four counters/static; no historical transfer."""
import pg7660_mq_pressure_post_v2 as previous
import pg7674_mq_redelivery_host as host

METHODS={
 'mqRedel001OnlySixApprovedQueuesAndThreeRedeliveryLabelsExistAtZero',
 'mqRedel002InitialDeliveryNeverCountsAndEachRedeliveryCountsExactlyOnce',
 'mqRedel003StandardDoesNotRegisterRetainOrIncrementAnyDetailedCounter',
 'mqRedel004NullModeDestinationAndOutOfRangeCountsNeverMutateExistingCounters',
 'mqRedel005PartialFactoryFailureKeepsSameProblemAndCallerOwnedRegistry',
 'mqRedel006IncrementBeforeAfterFailuresAreNotFormattedRetriedOrCompensated',
 'mqRedel007ConcurrentSamePairAndSeparateOwnerHaveExactIndependentCounts',
 'mqRedel008ForeignGaugeCannotBeReplacedOrCloseBorrowedRegistry'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7674-mq-redelivery-host-v1'
    post.OUT=post.host.BASE/'PG7676-mq-redelivery-post-v1'
    post.PRIVATE=post.host.W/'pg7676-mq-redelivery-post-v1'
    post.METHODS|=METHODS;post.NAMES.add(post.PREFIX+'MqRedeliveryMetricRecorder')
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=122;post.SOURCE_FILE_COUNT=30
    return post

if __name__=='__main__':
    host.previous.previous.previous.verify_inputs()
    configure().main()
