"""Independent154/19/38 Java/actual32 exact XML CRC four counter and static verification."""
import pg7874_api_query_collection_post as previous
import pg7892_mq_duration_host as host
METHODS=set(["mqTime001AllSixtyFourLiteralLayoutsBindApprovedFlowAndOnlyTwoPrimaryOutcomes","mqTime002FractionalSecondsCdfAndTwoMaximumSamplesUseIndependentFixedVectors","mqTime003ClosedOutcomeFactoriesAndUnknownLayoutCannotRegisterArbitraryNamespace","mqTime004NullNegativeAndStandardNeverRecordOrChooseDefaultMode","mqTime005PartialFactoryFailurePreservesIdentityPrefixAndCallerOwnership","mqTime006RecordFailureBeforeOrAfterIncrementNeverRetriesOrCompensates","mqTime007ConcurrentCountsSumsAndMaxUseIndependentIntegerVectorsAndSeparateLayoutOwners","mqTime008ForeignCounterCannotBecomeSummaryOrBeClosed"])
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7892-mq-duration-host-v1'
    post.OUT=post.host.BASE/'PG7894-mq-duration-post-v1'
    post.PRIVATE=post.host.W/'pg7894-mq-duration-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'MqProcessingDurationMetricRecorder',post.PREFIX+'MqProcessingDurationMetricRecorder$Outcome'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=154;post.SOURCE_FILE_COUNT=38
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
