"""Independent212 ordinary cases, positive52 scope/current source/single CRC session/four counters."""
import pg7550_protected_alert_post as previous
import pg7562_backup_health_host as host

METHODS={
 'backupMon001KnownNormalMissingAndPartialStayDistinctWithoutInventedEvents',
 'backupMon002FixedSeverityAndPartialAbnormalEvidenceAreIndependent',
 'backupMon003PartialOrMissingCannotBridgeWarningRecovery',
 'backupMon004CriticalNeedsTenMinutesAndConfirmedCauseDespiteLowerWarning',
 'backupMon005GapInvalidAndNullObservationsCannotFakeRecovery',
 'backupMon006ConcurrentSameOwnerKeepsExactCountAndOtherOwnerIndependent',
 'backupMon007CompletionGeneratedContractUsesIndependentBooleanHashAndText',
 'backupMon008EvaluationGeneratedContractUsesIndependentIdentityAndBooleanOracles'}

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7562-backup-health-host-v1'
    post.OUT=post.host.BASE/'PG7564-backup-health-post-v1'
    post.PRIVATE=post.host.W/'pg7564-backup-health-post-v1'
    post.METHODS|=METHODS
    post.NAMES|={post.PREFIX+'BackupHealthMonitor',post.PREFIX+'BackupHealthMonitor$Completion',post.PREFIX+'BackupHealthMonitor$Evaluation'}
    post.EXPECTED_SUITES[host.SUITES[-1]]=dict(tests=8,failures=0,errors=0,skipped=0)
    post.TOTAL_TESTS=212;post.SOURCE_FILE_COUNT=57
    return post

if __name__=='__main__':configure().main()
