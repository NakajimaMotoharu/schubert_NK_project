"""Ten Backup worker/copy/bundle ownership scopes,35 existing cases;864/101 expected."""
import pg5248_startup_view_selected as previous
import pg5200_morning_owner_selected as aliases

selected=previous.selected
PREFIX='batch:dev/codex/schubert/nk/batch/file/'
OUTERS={'BackupDatabaseWorker','BackupDatabaseCopy','BackupBundlePublisher'}
DEBUG={'BackupDatabaseWorker$Ports','BackupDatabaseWorker$NativePorts','BackupDatabaseCopy$Dump',
       'BackupBundlePublisher$Io','BackupBundlePublisher$NioIo'}
BACKUP={f'dev.codex.schubert.nk.batch.file.{name}Test':'batch' for name in OUTERS}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**BACKUP}


def main():
    configure()
    return selected.main(stem_override='pg5256-backup-worker',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
