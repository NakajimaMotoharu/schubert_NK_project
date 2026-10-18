"""Archive nullable stdio preowners and prebuilt nonrecursive all-terminal cleanup."""
import pg5380_nss_root_query_selected as previous

selected=previous.selected
aliases=previous.aliases
repetitions=previous.repetitions
PREFIX='batch:dev/codex/schubert/nk/batch/platform/'
FILES={'BackupArchiveProcess'}
OUTERS={'BackupArchiveProcess','BackupArchiveProcess$TerminalPlan','BackupArchiveProcess$StdIoOwner'}
ADDED={PREFIX+n+'.class' for n in ('BackupArchiveProcess$TerminalPlan','BackupArchiveProcess$StdIoOwner')}
REMOVED={PREFIX+'BackupArchiveProcess$StdinOwner.class'}
DEBUG={'BackupArchiveProcess$Work','BackupArchiveProcess$NativeStart','BackupArchiveProcess$NativeStart$Pipeline',
       'BackupArchiveProcess$NativeStart$Pending','BackupArchiveProcess$NativeStart$PendingHold'}
RELATED={'dev.codex.schubert.nk.batch.platform.BackupArchiveProcessTest':'batch'}
EXPECTED_MAIN=765


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+'BackupArchiveProcess.class'}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}
    selected.EXTRA_ADDED=set(ADDED)
    selected.EXTRA_REMOVED=set(REMOVED)


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


if __name__=='__main__':
    configure()
    raise SystemExit(selected.main(stem_override='pg5390-archive-pipeline',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases(),case_repetitions=repetitions()))
