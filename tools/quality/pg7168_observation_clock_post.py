"""Current91 original cases and all22 executable classes/metadata, no historical counter union."""
import pg7066_timed_filesystem_post as previous
import pg7086_registry_missing_post as missing
import pg7154_filesystem_health_post as health
import pg7166_observation_clock_host as host

METHODS={'obsClock001IndependentNanosAndActualUtcAreNotRebasedOrClamped',
 'obsClock002SignedOriginAndRegularLongWrapHaveFiveNanos',
 'obsClock003EpochMaximumAndOverflowHaveExplicitDifferentOutcomes',
 'obsClock004BackwardsTickDoesNotReadUtcCommitOrResetTheEpoch',
 'obsClock005SourceFailuresRemainUnformattedAndDoNotCommitFailedContexts',
 'obsClock006NullContractsDoNotTouchProvidersAndSnapshotsStayImmutable',
 'obsClock007ConcurrentContextsHaveUniqueMonotonicSnapshots',
 'obsClock008HealthConnectionBreaksClockAndUncheckedInputGapsAcrossBothApis'}


if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7166-observation-clock-host-v1'
    post.OUT=post.host.BASE/'PG7168-observation-clock-post-v1'
    post.PRIVATE=post.host.W/'pg7168-observation-clock-post-v1'
    post.METHODS|=missing.METHODS|health.METHODS|METHODS
    post.NAMES|={post.PREFIX+n for n in ('FilesystemHealthObservation','FilesystemHealthMonitor','MonitoringObservationClock')}
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3,10,8),strict=True)}
    post.TOTAL_TESTS=91;post.SOURCE_FILE_COUNT=27
    post.main()
