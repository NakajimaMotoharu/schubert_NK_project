"""Twelve Cleanup/Transfer/lock Directory owners and exact existing related suites."""
import pg5264_morning_backup_selected as previous

selected=previous.selected
aliases=previous.aliases
PREFIX=previous.PREFIX
OUTERS={'CleanupExpiryExecution','CleanupMaintenanceWork','CleanupNativeExecution','CleanupNativePreflight',
        'MaintenanceFileLock','TransferCleanup'}
DEBUG={'CleanupExpiryExecution$ExpiryWork','CleanupExpiryExecution$1','CleanupMaintenanceWork$AfterInspection',
       'CleanupMaintenanceWork$Inbox','CleanupMaintenanceWork$Transfer','CleanupNativePreflight$StopObservation',
       'MaintenanceFileLock$Metadata','MaintenanceFileLock$Snapshot','MaintenanceFileLock$Io','MaintenanceFileLock$NioIo',
       'MaintenanceFileLock$ViewOperation','MaintenanceFileLock$Identity','TransferCleanup$Outcome',
       'TransferCleanup$Guard','TransferCleanup$Counts'}
RELATED={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch'
         for name in ('CleanupExpiryExecution','CleanupMaintenanceWork','CleanupNativePreflight',
                      'MaintenanceFileLock','TransferCleanup','TransferCleanupFailure')}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5272-cleanup-factory',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
