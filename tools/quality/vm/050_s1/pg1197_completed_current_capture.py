"""New read-only full current seal after actual Root DONE/A01, no stop authority."""
import ast
import inspect
from pg1177_canonical_runtime_owner_proof import payload as library
from pg1195_completed_resume_a01 import guard
import pg1196_completed_rows_oracle as data
import pg1120_current_failed_capture as transport


def payload():
    s=library();s=s[:s.index('JAVA=420139')].replace('canonical-runtime-owner-proof-v1','completed-current-before-v1')
    tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='capture')
    s=s.replace(ast.get_source_segment(s,node),CAPTURE)
    a=s.index('def canonical_configuration(');s=s[:a]
    # Only aggregate row read adopts64MiB; all other command bounds remain pinned.
    s=s.replace("command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;'],33554432)","row_command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;'])")
    g=guard();end=g.rfind('print(json.dumps(units))');require=end>=0
    if not require:raise ValueError('fixed pure Root guard closure refused')
    g=g[:end]
    s+='\nDATA_SOURCE='+repr(inspect.getsource(data))+'\nGUARD_SOURCE='+repr(g)+'\n'+BODY
    ast.parse(s);return s


CAPTURE=r'''
def capture():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 witness=types.ModuleType('actual_same_root');exec(GUARD_SOURCE,witness.__dict__)
 us={u:show(u,FIELDS)for u in CAPTURE_UNITS}
 require({u for u,v in us.items()if v['MainPID']!='0'}=={'schubert-nk-api.service','schubert-nk-web.service','caddy.service','artemis.service'})
 broker=us['artemis.service'];require(broker['MainPID']=='441175'and broker['InvocationID']=='c874395201b94ae7b144e3a6bb2d3b8e'and broker['ActiveState']=='active'and broker['SubState']=='running'and not broker['Job'])
 p=pathlib.Path('/proc/441175');require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==5127657)
 actors={}
 for u,v in us.items():
  require(v['LoadState']=='loaded')
  if v['MainPID']=='0':kernel(u)
  else:
   p=pathlib.Path('/proc')/v['MainPID'];actors[u]={'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'cgroup':(p/'cgroup').read_text(),'process':{k:x.strip()for k,x in dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line).items()if k in {'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}}}
   require(actors[u]['cgroup']=='0::/system.slice/'+u+'\n')
 rs=rows();summary=data_oracle.after(SEALED['rows'],rs,RUN,'2026-10-10T17:15:39.000000Z',UPPER)
 durable={k:tree(pathlib.Path(min(v,key=len)))for k,v in SEALED['durable'].items()}
 for k in durable:
  if k!='originals':require(durable[k]==SEALED['durable'][k])
 original=durable['originals'];old=SEALED['durable']['originals'];root='/var/lib/schubert-nk/maintenance';done=root+'/attempts/'+ACT+'.done'
 require(set(original)==(set(old)-{root+'/active'})|{done})
 for path,value in old.items():
  if path==root+'/active':continue
  now=original[path]
  if path in {root,root+'/attempts'}:require(now['sha256']==value['sha256']and now['metadata'][:6]==value['metadata'][:6]and now['metadata'][7]>=value['metadata'][7]and now['metadata'][8]>=value['metadata'][8])
  else:require(now==value)
 require(original[done]['metadata'][2:7]==[0,0,stat.S_IFREG|0o600,1,140]and original[done]['sha256']=='7c286a3183c565cb25d87c1eb4476c3ad1db87628dd80ef3ee90e7f6cbd738cc')
 release=pathlib.Path('/opt/schubert-nk/current');current_path='/opt/schubert-nk/releases/0.1.0-PG1068';require(str(release.readlink())==current_path)
 now={name[len(current_path):].lstrip('/'):v for name,v in tree(pathlib.Path(current_path)).items()}
 ancestor_paths=['/','/opt','/opt/schubert-nk','/opt/schubert-nk/releases'];ancestor_names=['/','opt','schubert-nk','releases']
 ancestors=[{'name':name,'value':entry(pathlib.Path(path))}for name,path in zip(ancestor_names,ancestor_paths)]
 projected=held.project(before['heldWholeMetadata'][1],now,ancestors,'0.1.0-PG1068')
 old_release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG932')
 artifactSummary=artifacts.qualify(baseline['artifacts'],projected,now,(release/'RELEASE-MANIFEST.json').read_bytes(),lambda name:(old_release/name).read_bytes(),lambda name:(release/name).read_bytes(),'d5b00104280028d9ea81b44c1d1c805f3c2861ed','0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d')
 unitFiles={name:entry(pathlib.Path(name))for name in before['unitFiles']};require(unitFiles==before['unitFiles'])
 configuration={u:show(u,configuration_fields())for u in CAPTURE_UNITS}
 for unit,old in SEALED['configuration'].items():
  value=configuration[unit];require(set(value)==set(old)and all(value[k]==old[k]for k in old if k!='ExecStart'))
  a,b=exec_record(old['ExecStart']),exec_record(value['ExecStart']);require(a is not None and b is not None and a[:3]==b[:3])
 startup=pathlib.Path('/run/schubert-nk/startup');state=tree(startup)
 for path,value in SEALED['startup'].items():
  if path not in {str(startup),str(startup/'epoch.current')}:require(state[path]==value)
 privateBytes={str(p):p.read_bytes().hex()for p in startup.iterdir()}
 runtime=tree(pathlib.Path('/run/systemd/system'));require(runtime==SEALED['runtime'])
 journals={u:command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'-u',u,'--since','2026-10-10 12:40:16 UTC','-o','json','--no-pager']).hex()for u in CAPTURE_UNITS};JOURNAL_READS.append(journals)
 canonical={u:journal.project(bytes.fromhex(value)).hex()for u,value in journals.items()}
 native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
 require(all(not pathlib.Path('/proc',str(pid)).exists()for pid in [430851,420139,420168]))
 sql="select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0'])
 return{'units':us,'actors':actors,'rows':rs,'durable':durable,'trees':dict({k:v for k,v in durable.items()},startup=state,originals=original,backup=durable['backup'],native=native),'unitFiles':unitFiles,'configuration':configuration,'runtime':runtime,'startup':state,'privateBytes':privateBytes,'journals':canonical,'native':native,'source':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','manifestSha256':'0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','artifactSummary':artifactSummary,'genuineCompletion':witness.result,'pid1':witness.rows,'completionSha256':original[done]['sha256'],'run':RUN,'cutoff':CUTOFF,'activation':ACT,'current':current_path,'dataSummary':summary,'authority':False}
'''


BODY=r'''
import types
data_oracle=types.ModuleType('independent_current_rows');exec(DATA_SOURCE,data_oracle.__dict__)
def row_command(args):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 data_oracle.output_bound(p.returncode,len(p.stdout));return p.stdout
CAPTURE_UNITS=tuple(units)
old_path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/canonical-runtime-owner-handoff-v1/after.private.json')
old_raw=old_path.read_bytes();require(hashlib.sha256(old_raw).hexdigest()=='d218c5e294937078d6535b1871552a2bac1f4a3a81c8a46f47f0f018b79b8550');SEALED=json.loads(old_raw)
UPPER=datetime.datetime.now(datetime.timezone.utc).isoformat()
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in CAPTURE_UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 observed=capture();require(observed==capture());SAVE.mkdir(mode=0o700)
 with(SAVE/'before.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(observed,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 require(observed==capture())
 for i,read in enumerate(JOURNAL_READS):
  with(SAVE/('journal-read-'+str(i)+'.private.json')).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(read,f,sort_keys=True);f.flush();os.fsync(f.fileno())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateBeforeSha256':hashlib.sha256((SAVE/'before.private.json').read_bytes()).hexdigest(),'dataSummary':observed['dataSummary'],'genuineCompletion':observed['genuineCompletion'],'currentFourOwnedLive':True,'allOriginalsBackupOldSourcePreserved':True,'newMetadataReferencesNormalClose':True,'operationAuthority':False,'formalAccepted':False,'configurationWritesStartsStops0':True}))
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1197-completed-current-before-v1').replace('PG1120-current-failed-capture-v1','PG1197-completed-current-before-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload()
    exec(compile(s,'<full same current completed capture>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
