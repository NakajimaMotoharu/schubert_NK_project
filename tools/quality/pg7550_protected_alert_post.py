"""Independent current204/27, unchanged positive49 execution scope, no actual alarm operations."""
import pg7534_async_byte_unit_post as previous
import pg7549_protected_alert_host as host

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7548-protected-alert-host-v2'
    post.OUT=post.host.BASE/'PG7550-protected-alert-post-v1'
    post.PRIVATE=post.host.W/'pg7550-protected-alert-post-v1'
    post.METHODS|={'protectedAlert001AllKeysHonorNoAutomaticCloseDespiteConfirmedCause',
      'protectedAlert002ConcurrentNormalSamplesCannotRetireOrChangeProtectedEvent'}
    post.EXPECTED_SUITES['dev.codex.schubert.nk.batch.monitoring.AlertLifecycleTest']['tests']=12
    post.TOTAL_TESTS=204
    return post

if __name__=='__main__':configure().main()
