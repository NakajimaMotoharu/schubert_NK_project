"""Independent actual130/16 API25/CRC/four counters/static, no historical source successes combined."""
import pg7676_mq_redelivery_post as previous
import pg7690_mq_pressure_connection_host as host

METHODS={
 'mqConn001EachSuppliedResultPublishesAllSixValuesOnlyAfterReadCompletes',
 'mqConn002UnknownClearsOnlySelectedDestinationAndTrueZeroRecovers',
 'mqConn003RuntimeAndFatalReadFailuresClearSelectedValuesAndRethrowSameObjectOnce',
 'mqConn004StandardNeverReadsEvenFailingSourceAndAssemblyChecksAllNullModes',
 'mqConn005NullDestinationCannotEraseStateAndIllegalNullResultIsNotNormalUnknown',
 'mqConn006OwnedContenderIsBlockedUntilReadAndPublicationComplete',
 'mqConn007ParallelCallsAndSeparateOwnersKeepExactReturnedObservations',
 'mqConn008PartialAssemblyFailureNeverReadsSourceClosesRegistryOrRetries'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7690-mq-pressure-connection-host-v1'
    post.OUT=post.host.BASE/'PG7692-mq-pressure-connection-post-v1'
    post.PRIVATE=post.host.W/'pg7692-mq-pressure-connection-post-v1'
    post.METHODS|=METHODS;post.NAMES.add(post.PREFIX+'MqPressureMetricCollector')
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=130;post.SOURCE_FILE_COUNT=32
    return post

if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
