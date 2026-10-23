"""Exact original27 cases/11 executable classes; no legacy exec/session union."""
import pg7008_monitoring_mode_post as post
import pg7014_metric_catalog_post as catalog
import pg7018_alert_lifecycle_host as host

METHODS = {
 'alert001InitialNormalAndFirstWarningIdentity','alert002DedupEscalationAndNoAutomaticDowngrade',
 'alert003WarningFiveMinuteExactBoundary','alert004CriticalNeedsTenMinutesAndCauseConfirmation',
 'alert005AnyViolationRestartsContinuousNormalPeriod','alert006ClosedEventRetiredAndNewViolationStartsFresh',
 'alert007NullAndInvalidElapsedLeaveStateUnchanged','alert008WallClockJumpDoesNotShortenRecoveryOrOverflow',
 'alert009ConcurrentSameTickCountsAndPrivateMonitor','alert010AllClosedConditionServiceIdentities',
 'alertReg001PerKeyDedupIndependentIdentityAndImmutableOrder','alertReg002ExactlySeventyTwoKeysAndAllRecovery',
 'alertReg003MissingInputsDoNotChangeExistingKey','alertReg004ConcurrentCallersShareOneKeyOwner'}


if __name__ == '__main__':
    post.SLOT = host.SLOT
    post.RUN = 'PG7018-alert-lifecycle-host-v1'
    post.OUT = post.host.BASE/'PG7020-alert-lifecycle-post-v1'
    post.PRIVATE = post.host.W/'pg7020-alert-lifecycle-post-v1'
    post.NAMES = {post.PREFIX+n for n in (
      'MonitoringModePolicy','MonitoringModePolicy$DetailService','MetricContract','MetricContract$Kind',
      'AlertLifecycle','AlertLifecycle$Condition','AlertLifecycle$Service','AlertLifecycle$Severity',
      'AlertLifecycle$CauseClearance','AlertLifecycle$Event','AlertRegistry')}
    post.METHODS = post.METHODS | catalog.METHODS | METHODS
    post.EXPECTED_SUITES = {name:dict(tests=count,failures=0,errors=0,skipped=0)
                           for name,count in zip(host.SUITES,(7,6,10,4),strict=True)}
    post.TOTAL_TESTS = 27
    post.SOURCE_FILE_COUNT = 9
    post.main()
