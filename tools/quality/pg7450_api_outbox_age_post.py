"""Independent exact80/10 cases/current17 executable classes, same source/session/CRC/four counters."""
import pg7392_api_outbox_rows_post as previous
import pg7404_api_generated_contract_post as generated
import pg7448_api_outbox_age_host as host

METHODS={
 'outboxAge001CanonicalUnknownSeriesDoNotClaimObservedZero',
 'outboxAge002ExactFractionalSecondsAndSuppliedSnapshotAreIndependent',
 'outboxAge003ZeroMissingRecoveryAndMaximumDurationNeverOverflow',
 'outboxAge004StandardRegistersAndRetainsNothingButChecksNull',
 'outboxAge005NullNegativeAndUnknownModesCannotChangeExistingObservation',
 'outboxAge006OneOwnerPublishesWholeImmutableSnapshotsConcurrently',
 'outboxAge007PartialProviderFailureKeepsCallerResourcesAndFailureIdentity',
 'outboxAge008SeparateOwnersAndGeneratedValueContractsAreExact'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7448-api-outbox-age-host-v1'
    post.OUT=post.host.BASE/'PG7450-api-outbox-age-post-v1'
    post.PRIVATE=post.host.W/'pg7450-api-outbox-age-post-v1'
    post.METHODS|=generated.METHODS|METHODS
    post.NAMES|={post.PREFIX+'OutboxAgeMetricRecorder',post.PREFIX+'OutboxAgeMetricRecorder$Ages'}
    for name in host.SUITES[-2:]:post.EXPECTED_SUITES[name]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=80;post.SOURCE_FILE_COUNT=20
    return post

if __name__=='__main__':configure().main()
