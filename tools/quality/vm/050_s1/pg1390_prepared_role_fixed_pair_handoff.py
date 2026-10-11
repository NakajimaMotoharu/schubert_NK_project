"""Only PG1389-proven failed pair; keep already-created role and all originals."""
import ast
import pg1382_role_fixed_ref_handoff as previous
import pg1389_role_prepared_failed_pair_proof as proof
from pg1334_published_owned_stop_sources_v2 import SOURCE

PROOF='26d94b74170539a1c5701ea1a864f796f5614ce133ffff51b4c6929cd7c91f13'

def payload(seals):
    raw=previous.payload(seals)
    changes=((previous.PROOF,PROOF),('pg1381-role-failed-ref-pair-v1','pg1389-role-prepared-failed-pair-v1'),('pg1382-role-fixed-ref-handoff-v1','pg1390-prepared-role-fixed-pair-v1'),('PG1382-role-fixed-ref-handoff-v1','PG1390-prepared-role-fixed-pair-v1'),('PG1382_RECOVERY','PG1390_RECOVERY'),('841734','842917'),('8003102','8059022'),('841763','842946'),('8003222','8059148'),('59288d02dc262cc503775fc2202bca4dda052c5680629efe0ba606fc25a2182f','2696ad1a304c5578e0cc00eb0ea259b9997f98033e24f1424b887782bd4219c9'),('12426413c4d6ce3d3dc0bf4335a62aadb4bb65fca17f9d56b78c1d8273ec48ed','f71a6b434ce49a9a988d00175548d92daaece56905f6e7f412e959bb110f424a'),(':1.616973',':1.617058'))
    for old,new in changes:
        if old not in raw:raise ValueError('exact current prepared pair binding required')
        raw=raw.replace(old,new)
    actual=proof.payload(seals)
    replacement={n.name:ast.get_source_segment(actual,n)for n in ast.parse(actual).body if isinstance(n,ast.FunctionDef)and n.name in {'candidate','fixed_owner'}}
    parent=replacement['fixed_owner'].replace('def fixed_owner():','def parent_only():')
    start=parent.index(' kids=');end=parent.index(' q=',start)
    parent=parent[:start]+" require(not pathlib.Path('/proc/842946').exists()and all(not(t/'children').read_text().strip()for t in(p/'task').iterdir()))\n"+parent[end:]
    replacement['parent_only']=parent.replace("'child':child","'child':None")
    for n in reversed(ast.parse(raw).body):
        if isinstance(n,ast.FunctionDef)and n.name in replacement:
            lines=raw.splitlines(keepends=True);raw=''.join(lines[:n.lineno-1])+replacement[n.name]+'\n'+''.join(lines[n.end_lineno:])
    compile(raw,'<actual prepared role pair handoff>','exec');return raw

def main():
    env=dict(previous.proof.previous.previous.previous.previous.prior.prior.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    raw=previous.source().replace('pg1382-role-fixed-ref-handoff-v1','pg1390-prepared-role-fixed-pair-v1')
    exec(compile(raw,'<prepared role handoff transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
