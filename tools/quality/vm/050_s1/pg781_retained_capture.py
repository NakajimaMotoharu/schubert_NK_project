"""New-only retained779 capture; current server-session0 is not held JDBC success."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg780_retained_capture.py').read_text().replace('pg780-retained779-current-v1','pg781-retained779-current-v1')
    assert "['sudo','-n','-u','postgres','psql','-X','-qAt'"in raw
    raw=replace(raw,(("select jsonb_agg(jsonb_build_object(","select coalesce(jsonb_agg(jsonb_build_object("),
        ("l.objsubid=1 and l.granted)))from pg_stat_activity a where a.application_name in ('PG779-fixed-recovery','PG779-fixed-snapshot');", "l.objsubid=1 and l.granted))),'[]'::jsonb)from pg_stat_activity a where a.datname='schubert_nk'and a.backend_type='client backend'and a.pid<>pg_backend_pid();"),
        ("sessions=json.loads(db);assert len(sessions)==2 and sum(x['advisory']for x in sessions)==1", "sessions=json.loads(db);assert type(sessions)is list and sessions==[]"),
        ("'sameEpochInvalid':True,'old779NormalReturn':False", "'sameEpochInvalid':True,'serverSessionCount':0,'serverAdvisoryHeld':False,'jdbcObjectsHeldNotInferred':True,'old779NormalReturn':False")))
    raw=replace(raw,(("startup_bytes={p.name:p.read_bytes().hex()for p in startup.iterdir()};assert a==actor(3105271,14283385,'java')and b==actor(3105303,14283477,'refs')",r'''startup_bytes={p.name:p.read_bytes().hex()for p in startup.iterdir()}
def stable(value):
 status=dict(l.split(':',1)for l in value['status'].splitlines()if ':'in l)
 return {**{k:v for k,v in value.items()if k!='status'},'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid')}}
assert stable(a)==stable(actor(3105271,14283385,'java'))and stable(b)==stable(actor(3105303,14283477,'refs'))'''),))
    return raw


if __name__=='__main__':
    exec(compile(source(),'<new781 retained private capture>','exec'),{'__file__':str(R/'pg781_retained_capture.py'),'__name__':'__main__'})
