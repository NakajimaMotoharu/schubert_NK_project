"""New-only read-only PG758 failed cohort, full24/private byte capture; not authority."""
import ast
from pathlib import Path
from pg662_sources import replace
from pg772_failure_capture import source as prior

R = Path(__file__).resolve().parent

EXTRA = r'''
old760=base/'pg760-retention-post-v1/full-rows.private.json'
assert hashlib.sha256(old760.read_bytes()).hexdigest()=='01e2bab2a84d59b6ebe7a549c09f245fa46c8322a3c63ad7e09270b1399b9a1b'
expected_rows=json.loads(old760.read_bytes())['rows'];assert len(expected_rows)==24 and len(expected_rows['schubert.batch_runs'])==544
def rows():
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in sorted(expected_rows):
  assert all(c.isalnum()or c in '_.'for c in table)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from(select to_jsonb(t) j from "+table+" t)q;"
 value={}
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;'],33554432).splitlines():
  entry=json.loads(line);assert entry['table']not in value;value[entry['table']]=entry['rows']
 assert set(value)==set(expected_rows);return value
allrows=rows();assert allrows==expected_rows and rows()==allrows
security_keys=('Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs')
expected_live={'schubert-nk-api.service':('3063762','2dd9f106319e4c79995c8d6880c3f1a6','13884944','999','981','980 981 982 986'),
 'schubert-nk-web.service':('3066272','b49fd80a49a9408e8b8e13dd52f733b5','13886491','997','980','980 982 986'),
 'caddy.service':('3072633','b9c8ad2fabf244939367171499e0eac9','13889925','993','978','978'),
 'artemis.service':('2841798','47c9e398cfc043dfa7504bedbe486269','13746502','994','979','979')}
def identities(values):
 result={}
 for u,(pid,inv,ticks,uid,gid,groups)in expected_live.items():
  v=values[u];assert v['MainPID']==pid and v['InvocationID']==inv and v['ActiveState']=='active'and v['SubState']=='running'and v['ControlPID']=='0'and not v['Job']and v['actor']['ticks']==ticks
  p=pathlib.Path('/proc')/pid;status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l);authority={k:status[k].strip()for k in security_keys}
  assert authority['Uid'].split()==[uid]*4 and authority['Gid'].split()==[gid]*4 and authority['Groups']==groups and authority['NoNewPrivs']=='1'
  assert all(authority[k]=='0000000000000000'for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
  cg=(p/'cgroup').read_text();assert cg=='0::/system.slice/'+u+'\n'
  result[u]={'pid':pid,'invocation':inv,'ticks':int(ticks),'authority':authority,'cgroup':cg,'argvSha256':v['actor']['argvSha256']}
 return result
live=identities(a)
def configurations():
 fields='Id,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL,TimeoutStartUSec,TimeoutStopUSec,ExecStart,ExecStop,User,Group,SupplementaryGroups,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictAddressFamilies,ReadWritePaths,ReadOnlyPaths,Requires,After,FragmentPath,DropInPaths'
 return {u:command(['/usr/bin/systemctl','show',u,'--property='+fields]).decode()for u in units}
configuration=configurations();startup=pathlib.Path('/run/schubert-nk/startup');epochid=epoch['epoch_id']
assert epochid=='e9f11f1c-f087-458a-aad0-8c1e4e140571'and epoch['state']=='ISSUED'
current_names={p.name for p in startup.iterdir()if p.name.startswith(epochid)}
assert current_names=={epochid+s for s in ('.permit','.owner','.API.launch','.WEB.launch','.API.start.intent','.WEB.start.intent')}
assert len(list(startup.iterdir()))==41 and not (startup/'permit-start.intent').exists()
private_bytes={str(p):p.read_bytes()for d in (startup,pathlib.Path('/var/lib/schubert-nk/maintenance'))for p in d.rglob('*')if p.is_file()}
assert all(len(v)<=1048576 for v in private_bytes.values())
assert trees['startup']==tree(startup)and trees['originals']==tree(pathlib.Path('/var/lib/schubert-nk/maintenance'))and trees['backup']==tree(pathlib.Path('/srv/schubert-nk/backup'))
assert configuration==configurations()and live==identities(actors())and rows()==allrows
'''


def source():
    raw=prior().replace('pg772-failure-current758-v1','pg773-failure-full758-v1')
    raw=replace(raw, (("b=actors();assert all(a[u]", EXTRA+"\nb=actors();assert all(a[u]"),
        ("'epochFields':{k:epoch[k]", "'rows':allrows,'actors':live,'configuration':configuration,'startupNames':sorted(p.name for p in startup.iterdir()),'privateBytes':{k:v.hex()for k,v in private_bytes.items()},'epochFields':{k:epoch[k]"),
        ("'startsStopsWrites0':True", "'full24Preserved':True,'fullBatchRows':544,'currentStartupFiles':7,'allStartupFiles':41,'startsStopsWrites0':True")))
    return raw


def payload():
    return next(ast.literal_eval(n.value)for n in ast.parse(source()).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))


if __name__=='__main__':
    exec(compile(source(),'<new773 failed private full capture>','exec'),{'__file__':str(R/'pg773_failure_full.py'),'__name__':'__main__'})
