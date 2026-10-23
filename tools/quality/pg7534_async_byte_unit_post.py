"""Independent changed-source202 ordinary cases; byte/count dimensions never conflated."""
import pg7520_expiry_backlog_post as previous
import pg7532_async_byte_unit_host as host

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7532-async-byte-unit-host-v1'
    post.OUT=post.host.BASE/'PG7534-async-byte-unit-post-v1'
    post.PRIVATE=post.host.W/'pg7534-async-byte-unit-post-v1'
    post.METHODS|={'asyncByte001EngineUsesStorageBytesIndependentOfMessageCount',
      'asyncByte002ByteUsageInvariantsAndGeneratedContractsHaveIndependentOracles'}
    post.NAMES|={post.PREFIX+'AsyncQueueMonitor$ByteUsage'}
    for name in ('MonitoringPolicyEngineTest','AsyncQueueMonitorTest'):
        post.EXPECTED_SUITES['dev.codex.schubert.nk.batch.monitoring.'+name]['tests']+=1
    post.TOTAL_TESTS=202;post.SOURCE_FILE_COUNT=55
    return post

if __name__=='__main__':configure().main()
