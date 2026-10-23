"""Independent actual114/14 API22 four counters; no historical/Protocol counters transferred."""
import pg7630_api_inbox_replay_post as previous
import pg7644_mq_pressure_host as host

METHODS={
 'mqPress001ExactlySixFamiliesAndSixApprovedDestinationPairsStartUnknown',
 'mqPress002LiteralIndependentFieldsZeroAndMaximumHaveNoInventedSumOrCapacity',
 'mqPress003MissingIsNaNNotZeroAndCannotEraseOtherDestinationOrOldSnapshot',
 'mqPress004StandardRetainsNothingAndConfigurationOrNegativeSamplesAreNotNormalized',
 'mqPress005PartialFactoryAndForeignTypeFailuresKeepExactCallerRegistry',
 'mqPress006ConcurrentPublicationAndDifferentOwnersDoNotGrowOrShareState',
 'mqPress007NullBoundariesCannotClearPreviouslyAcceptedObservationInEitherMode',
 'mqPress008GeneratedSnapshotContractsUseIndependentLongBooleanFoldAndFixedText'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7644-mq-pressure-host-v1'
    post.OUT=post.host.BASE/'PG7646-mq-pressure-post-v1'
    post.PRIVATE=post.host.W/'pg7646-mq-pressure-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'MqPressureMetricRecorder',post.PREFIX+'MqPressureMetricRecorder$Snapshot'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=114;post.SOURCE_FILE_COUNT=28
    return post

if __name__=='__main__':
    host.previous.verify_inputs()
    configure().main()
