"""Exact73 original cases/19 real executable classes; no old-source coverage union."""
import pg7066_timed_filesystem_post as previous
import pg7084_registry_missing_host as host

METHODS={'monMissing001AllRegistryKeysRequireFreshRecovery',
 'monMissing002EngineBoundariesPreserveEachOwner','monMissing003ConcurrentAbsencePreservesImmutableSnapshot'}


if __name__=='__main__':
    post=previous.configure()
    post.SLOT=host.SLOT
    post.RUN='PG7084-registry-missing-host-v1'
    post.OUT=post.host.BASE/'PG7086-registry-missing-post-v1'
    post.PRIVATE=post.host.W/'pg7086-registry-missing-post-v1'
    post.METHODS|=METHODS
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(7,6,10,4,14,7,6,8,2,6,3),strict=True)}
    post.TOTAL_TESTS=73
    post.SOURCE_FILE_COUNT=22
    post.main()
