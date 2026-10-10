"""Current held stop-tool cohort/full32 private before, no recovery action."""
import ast
import inspect
from pathlib import Path
import pg1203_failed_stop_owner_proof as old
import pg1204_jvm_gc_append_oracle as gc
import pg1213_configuration_scope_bridge as bridge
import pg611_durable as durable
import pg1120_current_failed_capture as transport


def prefix():
    s=old.prefix().replace("failed-stop-owner-proof-v1'","full32-stop-owner-proof-v1'")
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)and n.name=='fixed_owner');s=s.replace(ast.get_source_segment(s,node),OWNERS)
    marker="require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0'])"
    capture_node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)and n.name=='capture')
    capture=ast.get_source_segment(s,capture_node)
    if capture.count(marker)!=1:raise ValueError('fixed owned database aggregate gate refused')
    s=s.replace(capture,capture.replace(marker,marker.replace("[b'0',b'0']","[b'1',b'1']")),1)
    for name,module in [('gc_oracle',gc),('bridge',bridge),('writer',durable)]:
        raw=inspect.getsource(module)
        if name=='bridge':raw=raw.replace('from pg847_configuration import FIELDS as FULL','FULL='+repr(bridge.FULL))
        s+='\n'+name+'=types.ModuleType('+repr(name)+');exec('+repr(raw)+','+name+'.__dict__)\n'
    from pg1198_current_stop_binding import generate
    from pg1198_current_stop_binding_test import fixture
    cfg=generate(fixture())['pg1198_configuration_capture.py']
    s+='\nconfig=types.ModuleType("full_configuration");exec('+repr(cfg)+',config.__dict__)\n'
    return s


OWNERS=r'''
COHORT={555802:(5659239,'22cb32f47743110124a6b3358f13aa19732fb2b9db201840044fa897ae9e9abe','/opt/jdk-25.0.4/bin/java',555800),555831:(5659344,'429b2078021809e285be498dcc2de5c82fc9e20c15bfb71ac1b8d9643bf520d3','/usr/bin/python3.14',555802)}
def fixed_owner():
 result={}
 for pid,(ticks,argv,exe,ppid)in COHORT.items():
  p=pathlib.Path('/proc')/str(pid);status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
  require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==argv and str((p/'exe').readlink())==exe)
  require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0']and int(status['PPid'])==ppid)
  kids={x for task in(p/'task').iterdir()for x in(task/'children').read_text().split()};require(kids==({'555831'}if pid==555802 else set()))
  daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==pid]
  require(names==([':1.311674']if pid==555831 else []));result[str(pid)]={'ticks':ticks,'argvSha256':argv,'children':sorted(kids),'bus':names}
 locks={}
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;a=md(path);matches=[]
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE','555802']:
    d=f[5].split(':')
    if len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(a[0]),os.minor(a[0]),a[1]):matches.append(row)
  require(a[2:6]==[0,0,stat.S_IFREG|0o600,1]and len(matches)==1);locks[name]=matches[0]
 sql="select count(*)from pg_stat_activity a where pid=555829 and datname='schubert_nk'and usename='schubert_batch'and application_name='PG998-native-stop'and state='idle in transaction'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.granted);"
 require(command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',sql]).strip()==b'1')
 logs=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1208-native-stop-v1');require({p.name for p in logs.iterdir()}=={'refs-prepare.private.log'})
 require(hashlib.sha256((logs/'refs-prepare.private.log').read_bytes()).hexdigest()=='45cb5b2d773a0f7296d88372096b44fe31e0eedc737d925d0096203a3c2e9345')
 result['locks']=locks;result['failureFiles']=tree(logs);result['ownedBackend']=555829;return result
def whole():
 owner=fixed_owner();v=capture();require(all(v[k]==completed_current[k]for k in v if k!='journals'));gc_oracle.qualify(completed_current['journals'],v['journals'])
 configs={};scope={}
 for u in CAPTURE_UNITS:
  value=config.complete_configuration(command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(bridge.FULL))]).decode(),u)
  configs[u],scope[u]=bridge.extend(v['configuration'][u],value,v['units'][u])
 v['historicalConfiguration']=v['configuration'];v['configuration']=configs;v['configurationScope']=scope
 require(owner==fixed_owner());return{'current':v,'owner':owner}
'''


def payload():
    s=prefix()+BODY;ast.parse(s);return s


BODY=r'''
sealed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/completed-current-before-v1/before.private.json').read_bytes()
require(hashlib.sha256(sealed).hexdigest()=='398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa');completed_current=json.loads(sealed)
try:
 for u in CAPTURE_UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 observed=whole();require(observed==whole());SAVE.mkdir(mode=0o700)
 writer.save(SAVE,'before.private.json',json.dumps(observed,sort_keys=True).encode());require(observed==whole())
 for i,raw_journal in enumerate(JOURNAL_READS):writer.save(SAVE,'journal-read-'+str(i)+'.private.json',json.dumps(raw_journal,sort_keys=True).encode())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'privateBeforeSha256':hashlib.sha256((SAVE/'before.private.json').read_bytes()).hexdigest(),'full32AllTenCaptured':True,'historical20AndState6Unchanged':True,'newConfigurationScopeFields':['After','ExecStop','FragmentPath','ReadOnlyPaths','Requires','RestrictAddressFamilies'],'fixedHeldOwnerDbRefBeforeStop':True,'signals0':True,'newMetadataReferencesNormalClose':True,'formalAccepted':False}))
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1214-full32-stop-owner-proof-v1').replace('PG1120-current-failed-capture-v1','PG1214-full32-stop-owner-proof-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<new full32 current held owner proof>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
