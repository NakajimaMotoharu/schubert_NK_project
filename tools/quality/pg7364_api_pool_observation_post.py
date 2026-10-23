"""Independent current48 cases, ten executable API classes and exact six auxiliary pins."""
import pg7350_api_pool_metric_post as previous
import pg7362_api_pool_observation_host as host

METHODS={
 'poolRead001FourBorrowedGettersHaveIndependentValuesAndExactCalls',
 'poolRead002TrueZeroWithPositiveMaximumIsKnownNotMissing',
 'poolRead003InvalidStatisticsRemainUnknownNotZero',
 'poolRead004NullOwnersAreRejectedBeforeAnyGetter',
 'poolRead005ProviderFailuresPreserveIdentityWithoutRetryOrLaterGetters',
 'poolRead006MaximumIntegersBecomeExactLongsWithoutSumOrWrap',
 'poolRead007ParallelOwnedInterfacesCannotShareMutableObservationState',
 'poolRead008LaterGetterValuesAndSeparateOwnersCannotMutateSnapshots',
 'poolConn001DebugPublishesCompleteBorrowedGetterValues',
 'poolConn002InvalidObservationClearsOldValuesAndTrueZeroRecovers',
 'poolConn003AllGetterFailuresBecomeUnknownAndKeepIdentityWithoutGraphWalk',
 'poolConn004StandardNeverCallsEvenFailingGettersOrRetainsDetails',
 'poolConn005InvalidBoundariesCannotMutateOrEraseExistingSnapshot',
 'poolConn006OneOwnerSerializesGettersThroughPublication',
 'poolConn007ParallelFakeSourcesHaveCompleteIndependentReturnedCounts',
 'poolConn008SeparateOwnersAndRepeatedCollectionCannotGrowSeriesOrControlPool'}

if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7362-api-pool-observation-host-v1'
    post.OUT=post.host.BASE/'PG7364-api-pool-observation-post-v1'
    post.PRIVATE=post.host.W/'pg7364-api-pool-observation-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+n for n in ('DbPoolMetricObservation','DbPoolMetricCollector')}
    for name in host.SUITES[4:]:post.EXPECTED_SUITES[name]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=48;post.SOURCE_FILE_COUNT=13
    post.EXTRA_AUXILIARY_JARS=host.DEPENDENCIES
    post.main()
