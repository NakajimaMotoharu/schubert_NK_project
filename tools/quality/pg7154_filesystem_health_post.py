"""Actual83 cases/all21 current executable classes, no historical source counter transfer."""
import pg7066_timed_filesystem_post as previous
import pg7086_registry_missing_post as missing
import pg7152_filesystem_health_host as host

METHODS={'fsInput001FixedIndependentByteTableReadsExactlyTwoValues',
 'fsInput002InvalidValuesAreUnknownWithoutClampingOrStickyFailure',
 'fsInput003CheckedIoFailureIsUnknownAndNeverFormattedOrRetried',
 'fsInput004UncheckedAndFatalRemainTheSameFailureNotNormalData',
 'fsInput005MaximumAndSingleByteTotalsDoNotOverflow',
 'fsInput006OneByteBeforeIntegerThresholdNeverRoundsUpAcrossIt',
 'fsInput007NullAndConcurrentIndependentReadsDoNotAcquireOwnership',
 'fsInput008ActualObservationPortDrivesWarningAndCriticalBoundaries',
 'fsInput009MissingIoAndInvalidStatsBreakRecoveryRatherThanClosingAlert',
 'fsInput010NullBackwardsGapAndConcurrentPollHaveOneSerializedOwner'}


if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7152-filesystem-health-host-v1'
    post.OUT=post.host.BASE/'PG7154-filesystem-health-post-v1'
    post.PRIVATE=post.host.W/'pg7154-filesystem-health-post-v1'
    post.METHODS|=missing.METHODS|METHODS
    post.NAMES|={post.PREFIX+n for n in ('FilesystemHealthObservation','FilesystemHealthMonitor')}
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3,10),strict=True)}
    post.TOTAL_TESTS=83;post.SOURCE_FILE_COUNT=25
    post.main()
