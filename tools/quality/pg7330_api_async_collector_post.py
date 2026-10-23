"""Independent current24 API cases/whole component five executable classes."""
import pg7316_api_async_count_post as previous
import pg7328_api_async_collector_host as host

METHODS={
 'asyncConn001DebugCollectPublishesOnlyAfterSuccessfulClose',
 'asyncConn002FailureClearsStaleSuccessAndTrueEmptyCanRecover',
 'asyncConn003EveryObservationFailureIsUnknownAndPropagatedOnce',
 'asyncConn004StandardNeverReadsOrRegistersButRejectsNull',
 'asyncConn005ConstructorInvariantsAndInvalidNullCannotErasePriorSuccess',
 'asyncConn006OwnerSerializesReadCloseAndPublication',
 'asyncConn007ParallelCallersAndIndependentOwnersHaveNoCrossState',
 'asyncConn008FailureGraphsAreNotWalkedAndNextSuccessRecovers'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7328-api-async-collector-host-v1'
    post.OUT=post.host.BASE/'PG7330-api-async-collector-post-v1'
    post.PRIVATE=post.host.W/'pg7330-api-async-collector-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'AsyncJobMetricCollector'}
    post.EXPECTED_SUITES[host.SUITES[2]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=24;post.SOURCE_FILE_COUNT=7
    return post

if __name__=='__main__':
    configure().main()
