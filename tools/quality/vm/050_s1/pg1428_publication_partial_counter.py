"""Observe partial L/M; never infer wrapper coverage from exceptional calls."""
import pg1427_publication_latest_counter as previous
from pg1426_publication_factory_selected import CHANGED

def partial(values):
    kinds={'LINE','METHOD','CLASS','BRANCH'}
    if type(values)is not dict or set(values)!=kinds or any(type(v)is not int or v<0 for v in values.values())or values['BRANCH']!=0 or values['CLASS']!=0:
        raise ValueError('explicit partial publication counters refused')
    return dict(values)

def source():
    raw=previous.source()
    old="require({k:counts[k]for k in kinds}=={'LINE':1,'METHOD':1,'CLASS':0,'BRANCH':0})"
    if raw.count(old)!=1:raise ValueError('one faulty inferred partial result required')
    raw=raw.replace(old,'partial({k:counts[k]for k in kinds})')
    raw=raw.replace('pg1427-publication-latest-counter-v1','pg1428-publication-partial-counter-v1').replace('PG1427-publication-latest-counter-v1','PG1428-publication-partial-counter-v1')
    compile(raw,'<actual partial counter observation>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.previous.previous.__dict__,CHANGED=CHANGED,partial=partial)
    exec(compile(source(),'<new partial counter>','exec'),env)
    raise SystemExit(env['main']())
