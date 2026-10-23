"""Independent174/21 XML/CRC/four counters/static of all actual36 executables, no Root."""
import pg7964_duration_extreme_post as previous
import pg7978_exact_duration_host as host
METHODS={
'exDur001IndependentBelowEqualAboveEveryFiniteBoundary',
'exDur002BothMixedExtremeOrdersKeepSmallSamplesAndFiniteSum',
'exDur003RejectedScalarInputsLeaveCompleteSnapshotUnchanged',
'exDur004SnapshotIsAtomicDefensiveAndDoesNotAliasMutableBuckets',
'exDur005EveryIncompatibleFactoryConfigurationFailsClosed',
'exDur006GenericRegistryAcceptedOnlyWhenDetailedObservationDisabled',
'exDur007UnrelatedSummaryAndCounterRemainNormalSdkOwnedMeters',
'exDur008ConstructorsRejectNullAndDurationStateNeverReadsClock',
'exDur009ConcurrentUpdatesAndSnapshotsHaveConsistentIndependentIdentity',
'exDur010AuxiliaryGaugeFactoryFailureRetainsCallerOwnershipAndIdentity'}
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7978-exact-duration-host-v1'
    post.OUT=post.host.BASE/'PG7980-exact-duration-post-v1'
    post.PRIVATE=post.host.W/'pg7980-exact-duration-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'ExactDurationMeterRegistry',post.PREFIX+'ExactDurationMeterRegistry$ExactSummary'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=10,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=174;post.SOURCE_FILE_COUNT=42
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
