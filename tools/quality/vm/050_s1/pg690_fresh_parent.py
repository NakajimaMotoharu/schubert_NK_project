"""New one-shot ordinary campaign on PG682, never resumes the preserved DONE."""
from pathlib import Path
import pg685_sources as profile

R=Path(__file__).resolve().parent


def source():
    raw=profile.bind((R/'pg626_fresh_parent.py').read_text())
    for old,new in (
        ('pg626-fresh-parent-v2','pg690-fresh-parent-v1'),
        ('11675ec02384a125f762014ebb1da251a2ab07c466aa8465bcd0f05ee284ce91','f69b52ee024ca670723d077dd34b20a2f62803f6575e4ba02d886d395f124187'),
        ('==492','==514'),("'originalBatchRows':492","'originalBatchRows':514"),
        ("'priorBatchRows':492","'priorBatchRows':514"),("'priorTodayRuns':10","'priorTodayRuns':32"),
        ("'priorToday10SuccessVerified':True","'priorToday32HistoryVerified':True"),
        ('pg626-backup-preserve-v1','pg689-backup-preserve-v1'),
        ('pg626-prior-seven-backups','pg689-prior-seven-backups'),
        ('pg626-prepare-v2','pg690-prepare-v1'),('pg627','pg691'),
        ('pg626_fresh_parent_contract.py','pg690_fresh_contract.py'),
        ("'pg626-' + mode + '-v2'","'pg690-' + mode + '-v1'"),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    assert 'pg626'not in raw and 'PG621'not in raw
    return raw


if __name__=='__main__':
    exec(compile(source(),'<new source ordinary campaign>','exec'),
         {'__file__':str(R/'pg690_fresh_parent.py'),'__name__':'__main__'})
