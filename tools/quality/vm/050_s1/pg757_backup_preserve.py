"""Current seven Backup private archive before PG750 ordinary retention; no server mutation."""
from pathlib import Path
from pg721_backup_preserve import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(),(
        ('pg721','pg757'),('pg717-completed-activate-v1','pg752-completed-activate-v1'),
        ('3849806f2d462004c9135ed29b914388bf17d903219a2dc65a73bf23764eed7a','301fd4e8c2801c5b6c2356ae789a19a7b474ed49559852667a428eaac80cf263'),
        ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<current seven private backups; no server writes>','exec'),{'__file__':str(R/'pg757_backup_preserve.py'),'__name__':'__main__'})
