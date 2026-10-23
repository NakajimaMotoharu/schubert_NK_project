"""Independent actual98/12/current20 classes exact source/session/CRC/four counters, static raw kept."""
import pg7464_api_outbox_repository_post as previous
import pg7476_api_outbox_connection_host as host

METHODS={
 'outboxConn001BothFamiliesPublishOnlyAfterAllSuccessfulClose',
 'outboxConn002FailureClearsBothFamiliesAndTrueEmptyQueryRecovers',
 'outboxConn003EveryObservationFailureIsUnknownAndPropagatesUnchangedOnce',
 'outboxConn004StandardDoesNotReadRegisterOrRetainButChecksBoundaryNull',
 'outboxConn005ConstructorAndBoundaryNullCannotErasePreviouslyAcceptedObservation',
 'outboxConn006OneOwnerSerializesReadCloseAndBothPublications',
 'outboxConn007ParallelCallersAndSeparateOwnersCannotCrossState',
 'outboxConn008PartialConstructionFailureRetainsCallerRegistryAndExactProblem'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7476-api-outbox-connection-host-v1'
    post.OUT=post.host.BASE/'PG7478-api-outbox-connection-post-v1'
    post.PRIVATE=post.host.W/'pg7478-api-outbox-connection-post-v1'
    post.METHODS|=METHODS;post.NAMES.add(post.PREFIX+'OutboxMetricCollector')
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=98;post.SOURCE_FILE_COUNT=24
    return post

if __name__=='__main__':configure().main()
