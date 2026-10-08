"""One new ordinary noargs campaign on completed current source, not resume."""
from pathlib import Path

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg626_fresh_parent.py').read_text()
    for old,new in (
        ('72fb7440697ee1048a5c0145055dc1cc3c577914','36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ('4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e','57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'),
        ('PG621','PG631'),('pg626-fresh-parent-v2','pg650-fresh-parent-v1'),
        ("guard['invalid_epoch']", "guard['completed_epoch']"),
        ('pg624-completed-activate-v1','pg647-runtime-retirement-v1'),
        ('11675ec02384a125f762014ebb1da251a2ab07c466aa8465bcd0f05ee284ce91','9435e98281c0295a9f85d26623d5595191eb849c8c5f1befb82f17ddd3701770'),
        ('==492','==504'),("'originalBatchRows':492","'originalBatchRows':504"),
        ("'priorBatchRows':492","'priorBatchRows':504"),("'priorTodayRuns':10","'priorTodayRuns':22"),
        ("'priorToday10SuccessVerified':True","'priorToday22HistoryVerified':True"),
        ('pg626-backup-preserve-v1','pg649-backup-preserve-v1'),
        ("preserved['priorFiles']==34 and preserved['priorEligibleBundles']==7", "preserved['priorFiles']==38 and preserved['priorEligibleBundles']==8"),
        ('pg626-prior-seven-backups','pg649-prior-eight-backups'),
        ('pg626-prepare-v2','pg650-prepare-v1'),
        ('pg627','pg651'), ('pg626_fresh_parent_contract.py','pg650_fresh_contract.py'),
        ("'pg626-' + mode + '-v2'", "'pg650-' + mode + '-v1'"),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    # Guest contract is self-contained: transport of the independent selector only.
    old="prefix += 'GUARD=' + repr((R / 'pg650_fresh_contract.py').read_text()) + '\\n'"
    new="prefix += 'GUARD=' + repr(guest_contract()) + '\\n'"
    assert raw.count(old)==1;raw=raw.replace(old,new)
    return raw.replace('pg650-fresh-parent-v1','pg650-fresh-parent-v2').replace('pg650-prepare-v1','pg650-prepare-v2').replace("'pg650-' + mode + '-v1'","'pg650-' + mode + '-v2'")


def guest_contract():
    import ast
    raw=(R/'pg650_fresh_contract.py').read_text()
    raw=raw.replace('from pg626_fresh_parent_contract import skipped_cleanup_oracle','')
    original=(R/'pg626_fresh_parent_contract.py').read_text()
    tree=ast.parse(original)
    nodes={n.name:ast.get_source_segment(original,n)for n in tree.body if isinstance(n,ast.FunctionDef)}
    raw=raw[:raw.index('def retention_upper(')]+nodes['skipped_cleanup_oracle']+'\n'+nodes['retention_upper']
    for old,new in (('len(names)==12 and len(possible)==7','len(names)==13 and len(possible)==8'),("'eligibleUpperBound':7","'eligibleUpperBound':8"),("'maximumEligibleAfterNew':8","'maximumEligibleAfterNew':9"),("'expectedRetentionDeletes':1","'expectedRetentionDeletes':2"),("'expectedDeleted':[possible[0]]","'expectedDeleted':possible[:2]")):
        assert raw.count(old)==1;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),str(R/'pg650_fresh_parent.py'),'exec'),{'__file__':str(R/'pg650_fresh_parent.py'),'__name__':'__main__','guest_contract':guest_contract})
