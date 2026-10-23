"""Independent146/18/36 Java/actual30 exact XML CRC counter and static verification."""
import pg7864_api_query_duration_post_v4 as previous
import pg7872_api_query_collection_host as host
METHODS=set(["dbConn001CompleteProviderResultIsPublishedOnlyAfterAcquisitionAndSameObjectReturned","dbConn002MissingObservationNeverInventsZeroOrOutcomeAndTrueZeroIsOneSuppliedEvent","dbConn003RuntimeErrorAndNullProviderResultPropagateWithoutInventedFailureSample","dbConn004StandardDoesNotReadProviderAndConstructorBoundaryNeverSubstitutesDefaults","dbConn005ImmutableObservationNullNegativeBoundaryAndFiveGeneratedContractsHaveIndependentOracle","dbConn006OwnedContenderBlocksUntilFirstObservationIsPublished","dbConn007ConcurrentSamplesUsePrecomputedIdentityInputsAndSeparateOwners","dbConn008RegistryFailureKeepsPartialEffectsOriginalProblemAndBorrowedOwnership"])
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7872-api-query-collection-host-v1'
    post.OUT=post.host.BASE/'PG7874-api-query-collection-post-v1'
    post.PRIVATE=post.host.W/'pg7874-api-query-collection-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'DbQueryDurationMetricCollector',post.PREFIX+'DbQueryDurationMetricCollector$Observation'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=146;post.SOURCE_FILE_COUNT=36
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
