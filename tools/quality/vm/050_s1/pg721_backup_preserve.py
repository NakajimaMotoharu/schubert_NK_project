"""Preserve current seven Backup bundles before new PG715 ordinary retention."""
from pathlib import Path
from pg689_backup_preserve import source as previous
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg689', 'pg721'), ('pg685-completed-activate-v1', 'pg717-completed-activate-v1'),
        ('f69b52ee024ca670723d077dd34b20a2f62803f6575e4ba02d886d395f124187',
         '3849806f2d462004c9135ed29b914388bf17d903219a2dc65a73bf23764eed7a'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f', '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
    ))


if __name__ == '__main__':
    exec(compile(source(), '<current Backup private archive>', 'exec'),
         {'__file__': str(R / 'pg721_backup_preserve.py'), '__name__': '__main__'})
