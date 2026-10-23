"""Necessary70-case verification after BUG1649 source fix, not original success replay."""
import pg7006_monitoring_pure_host as runner
import pg7064_timed_filesystem_host as original

SLOT=runner.host.W/'pg7068-timed-filesystem-host-v2'
SUITES=original.SUITES


if __name__=='__main__':
    runner.main(SLOT,SUITES)
