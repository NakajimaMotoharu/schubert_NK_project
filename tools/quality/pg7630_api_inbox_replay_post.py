"""Independent actual106/13, API21 four counters; protocol is an unmeasured dependency, not transferred PT."""
import pg7478_api_outbox_connection_post as previous
import pg7628_api_inbox_replay_host as host

METHODS={
 'inboxMet001DebugRegistersOnlyAllApprovedLayoutResultPairsAtZero',
 'inboxMet002EachSuppliedReplayIncrementsExactlyOnePairOnce',
 'inboxMet003StandardRegistersAndRecordsNoDetailedCounters',
 'inboxMet004NullUnknownAndInvalidModeCannotCreateLabelsOrChangeCounters',
 'inboxMet005PartialFactoryFailurePreservesExactProblemAndCallerRegistry',
 'inboxMet006IncrementFailuresAreNotRetriedCompensatedOrFormatted',
 'inboxMet007ConcurrentSuppliedEventsKeepExactCountsAndSeparateOwners',
 'inboxMet008ForeignNamespaceTypeCollisionCannotReplaceOrCloseCallerMeter'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7628-api-inbox-replay-host-v1'
    post.OUT=post.host.BASE/'PG7630-api-inbox-replay-post-v1'
    post.PRIVATE=post.host.W/'pg7630-api-inbox-replay-post-v1'
    post.METHODS|=METHODS;post.NAMES.add(post.PREFIX+'InboxReplayMetricRecorder')
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=106;post.SOURCE_FILE_COUNT=26
    post.EXTRA_PRODUCTION_DEPENDENCY_JARS={host.PROTOCOL_PATH:host.PROTOCOL_SHA}
    return post

if __name__=='__main__':
    host.verify_inputs()
    configure().main()
