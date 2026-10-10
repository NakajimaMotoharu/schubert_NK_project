"""SSC252 new-only nested once, explicit prior-scope effects/current FD strict."""
import ast
import datetime
import json
from pathlib import Path
from pg1108_cold_ordinary_once import payload as previous
from pg1041_cold_policy_diagnostic import W
from pg1051_cold_tree_preflight_v2 import dispatch


def payload():
    retired=json.loads((W/'pg1110-readonly-once-retirement-v1/manifest.safe.json').read_bytes())
    if retired['actualExit']!=0 or not retired['observed']['oldReadonlyActorGone']:raise ValueError('normal fixed readonly retirement required')
    raw=previous().replace('PG1108-cold-ordinary-once-v1','PG1111-nested-ordinary-once-v1').replace('PG1108-ordinary-cold-once-v1','PG1111-nested-ordinary-once-v1')
    raw=raw.replace("save = pathlib.Path('/var/lib/pgpt-s1-preservation/pg1108-ordinary-cold-once-v1')", "save = pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/nested-once-v1')")
    marker="def persist(name,value):"
    if raw.count(marker)!=1:raise ValueError('fixed nested once protocol refused')
    raw=raw.replace(marker,COMPARE+'\n'+marker)
    raw=raw.replace('assert ordinary_post()==before==ordinary_post()', 'assert cross_scope(before,ordinary_post())and cross_scope(before,ordinary_post())')
    raw=raw.replace('assert ordinary_post()==before\n', 'assert cross_scope(before,ordinary_post())\n')
    stamp=json.loads((W/'pg1106-ordinary-cold-before-v1/manifest.safe.json').read_bytes())['startedUTC']
    t=datetime.datetime.fromisoformat(stamp);begin=int(t.timestamp())*1000000000+t.microsecond*1000
    code=Path(__file__).with_name('pg1109_ordinary_cross_scope_contract.py').read_text()
    raw='CROSS_SOURCE='+repr(code)+'\nCROSS_BEGIN_NS='+repr(begin)+'\n'+raw
    ast.parse(raw);return raw


COMPARE=r'''
cross=types.ModuleType('explicit_cross_scope');exec(CROSS_SOURCE,cross.__dict__)
def cross_scope(before,actual):
 failed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1108-ordinary-cold-once-v1')
 assert env['metadata'](failed)[2:6]==[0,0,stat.S_IFDIR|0o700,2] and not list(failed.iterdir())and not os.listxattr(failed)
 assert not pathlib.Path('/proc/20312').exists()
 return cross.compare(before,actual,CROSS_BEGIN_NS,time.time_ns(),True)
'''


if __name__=='__main__':
    if not(W/'pg1112-watch-v1.started').exists()or(W/'pg1112-watch-v1.exit').exists():raise ValueError('new current observer required')
    watch=W/'pg1112-parent-watch-v1.private.jsonl'
    if not watch.exists()or watch.stat().st_size==0:raise ValueError('new observer first snapshot required')
    dispatch('PG1111-nested-ordinary-once-v1','pg1111-nested-ordinary-once-v1',payload())
