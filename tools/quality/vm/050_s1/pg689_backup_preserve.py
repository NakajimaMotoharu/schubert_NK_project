"""New-only full current seven Backup private archive, no server mutation."""
from pathlib import Path
import pg685_sources as profile

R = Path(__file__).resolve().parent


def source():
    raw=profile.bind((R/'pg626_backup_preserve.py').read_text())
    for old,new in (
        ('pg626','pg689'),
        ('11675ec02384a125f762014ebb1da251a2ab07c466aa8465bcd0f05ee284ce91','f69b52ee024ca670723d077dd34b20a2f62803f6575e4ba02d886d395f124187'),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),'<new-current private Backup archive>','exec'),
         {'__file__':str(R/'pg689_backup_preserve.py'),'__name__':'__main__'})
