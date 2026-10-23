"""Independent245/32/current60 classes, exact XML/session/CRC/four counters/static on this source."""
import pg7612_dlq_health_post as previous
import pg7710_observed_retention_host as host

METHODS={
 'retConf001ExactApprovedDebugAndStandardConfigurationsPassWithoutMutation',
 'retConf002DebugRejectsEachIndependentDayAndByteMismatchWithoutRounding',
 'retConf003MissingNeverBecomesValidStandardZeroAndNonzeroStandardIsDrift',
 'retConf004NegativeInvariantsAndNullOptionalAreRejectedNotUnknownSuccess',
 'retConf005MaximumValuesRemainExactAndCannotOverflowIntoApprovedLimits',
 'retConf006RetentionAndCompleteServiceObservationsRemainSeparateImmutableContracts',
 'retConf007ParallelModeVerificationCannotMutateOrShareOtherModesConfiguration',
 'retConf008GeneratedConfigurationUsesIndependentIntegerLongHashAndFixedTextOracles'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7710-observed-retention-host-v1'
    post.OUT=post.host.BASE/'PG7712-observed-retention-post-v1'
    post.PRIVATE=post.host.W/'pg7712-observed-retention-post-v1'
    post.METHODS|=METHODS;post.NAMES.add(post.PREFIX+'MonitoringModePolicy$RetentionConfiguration')
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=245;post.SOURCE_FILE_COUNT=64
    return post

if __name__=='__main__':configure().main()
