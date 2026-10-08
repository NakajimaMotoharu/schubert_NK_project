"""New-only private all-eight Backup archive; readonly, no retention authority."""
from pathlib import Path

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg626_backup_preserve.py').read_text()
    for old,new in (
        ('pg624-completed-activate-v1','pg647-runtime-retirement-v1'),
        ('11675ec02384a125f762014ebb1da251a2ab07c466aa8465bcd0f05ee284ce91','9435e98281c0295a9f85d26623d5595191eb849c8c5f1befb82f17ddd3701770'),
        ('pg626-prior-seven-backups','pg649-prior-eight-backups'),
        ('pg626-backup-preserve-v1','pg649-backup-preserve-v1'),
        ("'eligibleBundles':7", "'eligibleBundles':8"),
        ("'priorEligibleBundles':7", "'priorEligibleBundles':8"),
        ('72fb7440697ee1048a5c0145055dc1cc3c577914','36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('len(directories)==12 and len(regular)==35 and len(members)==47','len(directories)==13 and len(regular)==39 and len(members)==52'),
    ):
        expected=2 if old=='pg626-backup-preserve-v1' else 1
        assert raw.count(old)==expected,old;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),str(R/'pg649_backup_preserve.py'),'exec'),{'__file__':str(R/'pg649_backup_preserve.py'),'__name__':'__main__'})
