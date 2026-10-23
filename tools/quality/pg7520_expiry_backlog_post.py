"""Independent200/27 cases/current48 positive classes, same source/CRC/session/four counters."""
import pg7506_async_queue_post as previous
import pg7518_expiry_backlog_host as host

METHODS={
 'expiryMon001KnownNormalAndUnknownDoNotInventAnEvent',
 'expiryMon002ExactCountBoundariesHaveFixedSeverityAndKey',
 'expiryMon003MissingBreaksWarningRecoveryWithoutErasingOldEvent',
 'expiryMon004CriticalStaysStickyUntilTenNormalMinutesAndCauseConfirmed',
 'expiryMon005ExplicitGapRestartsTheFiveMinuteWarningRecovery',
 'expiryMon006NullNegativeAndReversedTimeCannotChangeAcceptedEvent',
 'expiryMon007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts',
 'expiryMon008GeneratedEvaluationContractsUseIndependentBooleanAndIdentityHashes'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7518-expiry-backlog-host-v1'
    post.OUT=post.host.BASE/'PG7520-expiry-backlog-post-v1'
    post.PRIVATE=post.host.W/'pg7520-expiry-backlog-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'ExpiryBacklogMonitor',post.PREFIX+'ExpiryBacklogMonitor$Evaluation'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=200;post.SOURCE_FILE_COUNT=55
    return post

if __name__=='__main__':configure().main()
