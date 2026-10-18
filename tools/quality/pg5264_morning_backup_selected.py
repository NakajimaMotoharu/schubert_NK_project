"""Nine Morning Backup ownership candidates; existing four related suites, native not imported."""
import pg5256_backup_worker_selected as previous

selected=previous.selected
aliases=previous.aliases
PREFIX=previous.PREFIX
OUTERS={'MorningBackupArtifacts','MorningBackupRetention','MorningBackupReuse'}
DEBUG={'MorningBackupArtifacts$Work','MorningBackupArtifacts$Writer','MorningBackupRetention$Mode',
       'MorningBackupRetention$Work','MorningBackupRetention$Result','MorningBackupReuse$Continuation'}
RELATED={f'dev.codex.schubert.nk.batch.file.MorningBackup{name}Test':'batch'
         for name in ('Metadata','Catalog','InputMode','Retention')}


def configure():
    previous.configure()
    selected.EXTRA_CHANGED|={PREFIX+n+'.class' for n in OUTERS}
    selected.EXTRA_DEBUG|={PREFIX+n+'.class' for n in DEBUG}


def extra_suites():
    return {**previous.extra_suites(),**RELATED}


def main():
    configure()
    return selected.main(stem_override='pg5264-morning-backup',version_override='v1',
        extra_suites=extra_suites(),case_name_aliases=aliases.invocation_aliases())


if __name__=='__main__':raise SystemExit(main())
