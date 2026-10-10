"""SSC253 proven three siblings and live current observer, one new nested start."""
import ast
import hashlib
import json
from pathlib import Path
from pg1111_nested_ordinary_once import payload as previous
from pg1041_cold_policy_diagnostic import W,P
from pg1051_cold_tree_preflight_v2 import dispatch


def payload():
    m=json.loads((W/'pg1114-readonly-nested-retirement-v1/manifest.safe.json').read_bytes())
    if m['actualExit']!=0 or not m['observed']['oldReadonlyActorGone']:raise ValueError('normal fixed second readonly retirement required')
    expected={'pg1108-ordinary-cold-once-v1':{}}
    for tag in ('pg1107','pg1112'):
        stage=json.loads((W/(tag+'-stage-v1.safe.json')).read_bytes())
        if stage['actualExit']!=0 or stage['source']!='d5b00104280028d9ea81b44c1d1c805f3c2861ed':raise ValueError('qualified actual observer stage required')
        bundle=P/(tag+'-observer-stage-v1')
        expected[tag+'-observer-v1']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in bundle.iterdir()}
        if set(expected[tag+'-observer-v1'])!={tag+'_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'}:raise ValueError('fixed observer source closure refused')
    raw=previous().replace('PG1111-nested-ordinary-once-v1','PG1115-proven-nested-ordinary-once-v1').replace('nested-once-v1','proven-nested-once-v1')
    old="failed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1108-ordinary-cold-once-v1')"
    if raw.count(old)!=1:raise ValueError('fixed three-directory proof insertion refused')
    raw=raw.replace(old,old+"\n observed=sibling_proof.proof(pathlib.Path('/var/lib/pgpt-s1-preservation'),SIBLINGS)\n assert observed==SIBLINGS\n assert not pathlib.Path('/proc/134103').exists()")
    code=Path(__file__).with_name('pg1113_fixed_private_sibling_proof.py').read_text()
    code=code.replace('from pg1090_cold_finite_capture import metadata','metadata=io.metadata')
    marker="cross=types.ModuleType('explicit_cross_scope');exec(CROSS_SOURCE,cross.__dict__)"
    if raw.count(marker)!=1:raise ValueError('fixed sibling module insertion refused')
    raw=raw.replace(marker,marker+"\nsibling_proof=types.ModuleType('fixed_siblings');sibling_proof.io=io;exec(SIBLING_SOURCE,sibling_proof.__dict__)")
    # Actual current observer generation is fixed before start, not inferred from
    # old recorded PID or another observer's successful stage.
    raw=raw.replace('assert cross_scope(before,ordinary_post())and cross_scope(before,ordinary_post())',
                    "current_watch();assert cross_scope(before,ordinary_post())and cross_scope(before,ordinary_post())")
    raw=raw.replace('assert cross_scope(before,ordinary_post())\n phase=', 'current_watch();assert cross_scope(before,ordinary_post())\n phase=')
    marker='def persist(name,value):'
    raw=raw.replace(marker,WATCH+'\n'+marker)
    raw='SIBLINGS='+repr(expected)+'\nSIBLING_SOURCE='+repr(code)+'\n'+raw
    ast.parse(raw);return raw


WATCH=r'''
def current_watch():
 p=pathlib.Path('/proc/131494');parts=(p/'stat').read_text().rpartition(')')[2].split()
 assert int(parts[19])==3380839 and str((p/'exe').readlink())=='/usr/bin/python3.14'
 assert hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='01e70c3acbb5c30933d91a9e212edc6c9439a804eb67d5c4021276762d6dff46'
 s=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 assert s['Uid'].split()==s['Gid'].split()==['0']*4
 for child in {int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}:
  q=pathlib.Path('/proc')/str(child)
  try:assert str((q/'exe').readlink())=='/usr/bin/systemctl'
  except FileNotFoundError:pass # Finite read-only systemctl may exit during observation.
'''


if __name__=='__main__':
    if not(W/'pg1112-watch-v1.started').exists()or(W/'pg1112-watch-v1.exit').exists():raise ValueError('live current observer required')
    p=W/'pg1112-parent-watch-v1.private.jsonl'
    if not p.exists()or p.stat().st_size==0:raise ValueError('new observer first snapshot required')
    dispatch('PG1115-proven-nested-ordinary-once-v1','pg1115-proven-nested-ordinary-once-v1',payload())
