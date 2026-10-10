"""Current newrun full capture; session oracle only, whole business not inferred."""
import ast
import inspect
import json
from pathlib import Path
import re
import pg1245_fresh_completed_capture_v2 as previous
import pg1222_completed_retirement_preflight as transport
from pg1322_published_root_done_receipt import payload as receipt
from pg1242_fresh_ordinary_done_receipt import payload as old_receipt
from pg1293_completed_unused_stage_sources import SOURCE,DIGEST

BEFORE='3cb4a2cc52eed5e6fce68aa551c2af9ab65692ef0d5c5d7af9409a761cdecac9'
ROLES={'schubert-nk-api.service','schubert-nk-web.service','caddy.service','artemis.service'}


def compose(owned,end):
    if type(owned)is not dict or set(owned)!=ROLES or type(end)is not int or not 73654946447<=end<=75454946447:
        raise ValueError('current completed ownership tuple required')
    for v in owned.values():
        if type(v)is not tuple or len(v)!=3 or type(v[0])is not str or not v[0].isdigit()or int(v[0])<=0 or type(v[1])is not str or re.fullmatch(r'[0-9a-f]{32}',v[1])is None or type(v[2])is not int or v[2]<=7365494:
            raise ValueError('new current ordinary actor identity required')
    code=previous.payload()
    old_guard=old_receipt()
    old_guard=old_guard[:old_guard.index("private=Path('/var/lib/pgpt-s1-preservation/pg1242-fresh-ordinary-done-receipt-v1')")]
    new_guard=receipt();new_guard=new_guard[:new_guard.index("private=Path('/var/lib/pgpt-s1-preservation/pg1322-published-root-done-receipt-v1')")]
    if code.count(repr(old_guard))!=1:raise ValueError('one strict current receipt closure required')
    code=code.replace(repr(old_guard),repr(new_guard))
    old_owned=next(n for n in ast.parse(code).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='OWNED'for t in n.targets))
    code=code.replace(ast.get_source_segment(code,old_owned),'OWNED='+repr(owned))
    replacements=[('pg1238-fresh-day-ordinary-before-v1','pg1319-published-ordinary-before-v1'),
      ('57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e',BEFORE),
      ('62400649336',str(end)),('0.1.0-PG1068','0.1.0-PG1292'),
      ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',DIGEST),
      ('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE),
      ('9f651096-aef9-4fba-90b0-a653e99f035a','d2e3a86f-27a4-4c2a-be21-b512eebf1216'),
      ('2026-10-10T20:03:22.718197Z','2026-10-10T23:30:23.481632Z'),
      ('27accac0-c118-4c98-9244-02625a2d88a7','841b507c-2713-4ffe-8882-68f5fb3f87f5'),
      ('fresh-completed-capture-v2','published-completed-capture-v1')]
    for old,new in replacements:
        if old not in code:raise ValueError('fixed whole current capture boundary required')
        code=code.replace(old,new)
    code=code.replace("'businessFullOraclePending':True","'businessFullOraclePending':True,'dailyInspectorSkipNotNewNative':True")
    compile(code,'<actual new-source full32 captured cohort>','exec');return code


def ownership():
    receipt_value=json.loads((transport.W/'pg1322-published-root-done-receipt-v1.safe.json').read_bytes())
    if receipt_value['actualExit']!=0 or receipt_value['source']!=SOURCE:raise ValueError('genuine same-source DONE required')
    frames=[json.loads(line)for line in(transport.W/'pg1318-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    if not any(f.get('ready')=='api'and f.get('sameRootOrdinary')and f.get('sameParent')for f in frames)or not any(f.get('ready')=='web'and f.get('sameRootOrdinary')and f.get('sameParent')for f in frames)or not any(f.get('caddyTlsLogin200')for f in frames):
        raise ValueError('genuine sameRoot ordinary ready/TLS observations required')
    state=next(f['states']for f in reversed(frames)if 'states'in f)
    owned={u:(state[r]['MainPID'],state[r]['InvocationID'],state[r]['startTicks'])for r,u in [('api','schubert-nk-api.service'),('web','schubert-nk-web.service'),('caddy','caddy.service')]}
    # This exact Artemis generation was independently observed live under1320.
    owned['artemis.service']=('715021','1e638b051f644578ac4d6459e6845fbb',7377871)
    return owned,receipt_value['receipt']['endMonotonicUs']


def payload():return compose(*ownership())


def main():
    env=dict(transport.__dict__,payload=payload)
    code=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1323-published-completed-capture-v1')
    exec(compile(code,'<new fullcurrent capture transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
