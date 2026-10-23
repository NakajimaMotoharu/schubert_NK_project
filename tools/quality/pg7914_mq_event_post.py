"""Independent162/20/40 Java/actual34 XML/CRC/four counters/static verifier."""
import pg7894_mq_duration_post as previous
import pg7912_mq_event_host as host
METHODS=set(["mqEvent001EveryLiteralLayoutAddressAndSevenStageTupleHasOnlyApprovedLabels","mqEvent002EachSuppliedStageIncrementsOnceAndOtherOwnersStayUnchanged","mqEvent003SevenTypedStageMappingsAndGeneratedFactoriesRejectUnknownOrNull","mqEvent004NullUnknownLayoutAndModeNeverFallBackAndStandardStoresNoEvents","mqEvent005PartialFactoryFailureKeepsOriginalIdentityAndCallerRegistryOwnership","mqEvent006IncrementFailureBeforeOrAfterEffectNeverRetriesCompensatesOrCloses","mqEvent007ConcurrentCountsUsePrecomputedStageOwnerVectorsAndSeparateRegistry","mqEvent008ForeignGaugeCannotBecomeCounterAndKeepsIdentityValueAndOwnership"])
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7912-mq-event-host-v1'
    post.OUT=post.host.BASE/'PG7914-mq-event-post-v1'
    post.PRIVATE=post.host.W/'pg7914-mq-event-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'MqMessageMetricRecorder',post.PREFIX+'MqMessageMetricRecorder$Stage'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=162;post.SOURCE_FILE_COUNT=40
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
