"""Independent current544 full21/pairmarkers post; source/operator/actor from actual768."""
import json
from pathlib import Path
import re
from pg738_final import source as previous
from pg768_sources import current,actual
from pg662_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source(proof,baseline,meta):
    assert type(meta)is dict and type(meta.get('actualExit'))is int and meta['actualExit']==0
    assert type(meta['batchRows'])is int and meta['batchRows']==544 and meta['unitExit20']is True and meta['allNewScopesReturnedNormally']is True
    for field in ('beforeSha256','afterSha256'):assert type(meta[field])is str and re.fullmatch('[0-9a-f]{64}',meta[field])
    assert type(meta['invocation'])is str and re.fullmatch('(?!0{32}$)[0-9a-f]{32}',meta['invocation'])
    for field in ('pid','ticks','pid1Job'):assert type(meta[field])is str and re.fullmatch('[1-9][0-9]*',meta[field])
    start,end=meta['startMonotonicUs'],meta['endMonotonicUs']
    assert type(start)is int and type(end)is int and 0<start<end<=start+30000000
    assert type(meta['elapsedSeconds'])in (int,float) and meta['elapsedSeconds']==(end-start)/1000000
    raw=current(previous(),proof,baseline)
    raw=replace(raw,(
        ('pg738','pg769'),('PG738','PG769'),('pg715-manifest.sig','pg750-manifest.sig'),
        ('82316ed36abbedd2f85f1e26ca35cd2f10e4c1ac5c7deabc4454bcc5203257d4',meta['beforeSha256']),
        ('25e00f13202b08b8db34a8c95b77933ff44cd71d5c37de0fa3cc9aacd5c0609e',meta['afterSha256']),
        ('0d42d02df3a44b7bb036140f6cc076cf',meta['invocation']),
        ('130424890693',str(start)),('130426534781',str(end)),('130454890693',str(start+30000000)),
        ('2793207',meta['pid']),('13042489',meta['ticks']),('138755',meta['pid1Job']),
        ("'batchRows':534","'batchRows':544"),('1.644088',repr(meta['elapsedSeconds'])),
        ('from pg535_bootstrap_contract import UNIT,normal20','from pg535_bootstrap_contract import UNIT,normal20,native_tree,completion_messages'),
        ("pid1=[json.loads(line)","native_tree(b['native'],a['native'],actor['invocation'])\ncompletion_messages([json.loads(line).get('MESSAGE')for line in strict(proof/'journal.private.jsonl',0o600,4194304).splitlines()])\npid1=[json.loads(line)")))
    return raw


if __name__=='__main__':
    proof,baseline=actual();meta=json.loads((W/'pg769-actual-admin-meta-v1.safe.json').read_bytes())
    exec(compile(source(proof,baseline,meta),'<current768 full21pairpost>','exec'),{'__file__':str(R/'pg769_final.py'),'__name__':'__main__'})
