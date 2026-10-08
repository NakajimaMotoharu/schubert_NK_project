"""SSC225: current source separate existing-only Bootstrap input generation/normal scopes."""
import ast,datetime,hashlib,json,os,pathlib,re,secrets,stat,subprocess,sys,time
import dbus
from pg535_bootstrap_contract import normal20,same_terminal_cohort,credential_tree,native_tree,retire_no_replace,UNIT,SOURCES
from pg536_bootstrap_execution_contract import configuration as history_configuration
from pg529_dependency_graph import dependency_graph
from pg569_parent_join import completed_journal
from pg570_directory_identity import identity,held_directory,fully_absent
from pg559_terminal_refs import peer_query,peer_counts_valid,namespace_valid
from pg457_stable_actor import stable_actor,ENTRIES
ENTRY='dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain';ENTRIES.add(ENTRY)
CREDS=pathlib.Path('/etc/schubert-nk/credentials')
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
MODE=None
SAVE=None
def require(value):
 if not value:raise ValueError('current existing-only Bootstrap proof refused')
def main():
 global MODE,SAVE
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]in('verify','execute')and sys.argv[2].isdigit())
 MODE=sys.argv[1];backend=int(sys.argv[2]);os.umask(0o077)
 SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg570-bootstrap-'+('verify'if MODE=='verify'else'existing')+'-v1')
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
 require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 source=ast.parse(raw);names={'command','metadata','strict','owner','show','tree','configuration_fields','kernel'}
 definitions=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names))
 constants=[n for n in source.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):return ast.copy_location(ast.Constant(b'Pg570BootstrapExisting'),n)if n.value==b'Pg480BackupRecovery'else n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code)
 sealed={'datetime':datetime,'hashlib':hashlib,'json':json,'os':os,'pathlib':pathlib,'re':re,'stat':stat,'subprocess':subprocess,'sys':sys,'time':time,'require':require}
 exec(compile(code,'<sealed fixed owner>','exec'),sealed)
 command,metadata,strict,owner,show,tree,cfg,kernel,units,fields=(sealed[n]for n in ('command','metadata','strict','owner','show','tree','configuration_fields','kernel','UNITS','FIELDS'))
 require(SAVE.is_dir()and metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and {p.name for p in SAVE.iterdir()}=={'refs-prepare.private.log'})
 baseline_path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg559-terminal-readback-v2/after.private.json')
 base=strict(baseline_path,0o600,33554432);require(hashlib.sha256(base).hexdigest()=='23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677');baseline=json.loads(base)
 require(len(baseline['units'])==10 and len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==472)
 require(len(baseline['rows']['schubert.app_users'])==1 and baseline['rows']['schubert.app_users'][0]['role']=='ADMIN')
 held=owner();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 for unit in units:manager.RefUnit(unit);refs.append(unit)
 terminal=None;native_invocation=None;prepared={};synthetic={};actor=None
 credentials_before=tree(CREDS)
 require(all(str(CREDS/name)not in credentials_before for name in SOURCES))
 require(show(UNIT,{'TimeoutStartUSec'})['TimeoutStartUSec']=='30s')
 last_dependencies={}
 def connection(present):
  q=peer_query(backend).replace('PG559-terminal-readback','PG570-bootstrap-guard')
  require(peer_counts_valid(present,command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()))
 def snapshot(present):
  require(owner()==held);connection(present)
  current={unit:show(unit,fields)for unit in units};same_terminal_cohort(baseline['units'],current,terminal)
  for unit,v in current.items():require(v['MainPID']==v['ControlPID']=='0'and v['Job']==''and v['ActiveState']in('inactive','failed'));kernel(unit)
  configuration={unit:show(unit,cfg())for unit in units}
  if terminal is None:require(configuration==baseline['configuration'])
  else:
   require(set(configuration)==set(baseline['configuration']))
   for unit,previous in baseline['configuration'].items():
    if unit!=UNIT:require(configuration[unit]==previous)
    else:
     stamps=show(UNIT,{'ExecMainStartTimestamp','ExecMainExitTimestamp'})
     require(history_configuration(previous,configuration[unit],terminal,actor,stamps['ExecMainStartTimestamp'],stamps['ExecMainExitTimestamp']))
  raw_dependencies={unit:show(unit,{'Requires','Before','After','PartOf','BindsTo'})for unit in units}
  graph=dependency_graph(raw_dependencies,units);require(graph==baseline['dependencies']);last_dependencies.clear();last_dependencies.update(raw_dependencies)
  parent=command(['journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=075ad6644b284056a6cccf7af252519b','-o','json','--no-pager'])
  receipt=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/12f1af04-180e-405c-8738-853bbd875443.done')
  parent_rows,parent_receipt=completed_journal(parent,strict(receipt,0o600,4096))
  require(parent_receipt['endMonotonicUs']==46382089521 and parent_rows==baseline['parentPid1'])
  query="begin isolation level repeatable read read only;set local timezone='UTC';";data={}
  for table in baseline['rows']:
   require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',table)is not None)
   query+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from(select to_jsonb(t)j from "+table+" t)q;"
  for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',query+'commit;']).splitlines():
   row=json.loads(line);require(row['table']not in data);data[row['table']]=row['rows']
  require(data==baseline['rows'])
  trees={k:tree(pathlib.Path(p))for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('native','/run/schubert-nk/pt-coverage'),('oldProofs','/var/lib/pgpt-s1-preservation/pg557-native-stop-v1')]}
  require(all(v==baseline[k]for k,v in trees.items()if k!='native'))
  native_tree(baseline['native'],trees['native'],native_invocation)
  credential_tree(credentials_before,tree(CREDS),prepared)
  paths={**{n:pathlib.Path('/run/schubert-nk')/n for n in ('backup-request','cleanup-request','expiry-request')},'runtime-parent':pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')}
  namespace={n:{'metadata':metadata(p),'entries':sorted(c.name for c in p.iterdir()),'xattrs':os.listxattr(p)}for n,p in paths.items()}
  require(not os.path.lexists(paths['runtime-parent']/'pg492-once-resume.conf')and namespace_valid(namespace)and namespace==baseline['namespace'])
  require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG548')
  require(current=={unit:show(unit,fields)for unit in units}and owner()==held);connection(present)
  return {'units':current,'configuration':configuration,'rows':data,'dependencies':graph,'namespace':namespace,'credentials':tree(CREDS),'parentPid1':baseline['parentPid1'],**trees}
 credsfd=os.open(CREDS,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);savefd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 creds_identity=identity(os.fstat(credsfd));save_identity=identity(os.fstat(savefd))
 require(all(v[2:5]==(0,0,stat.S_IFDIR|0o700)for v in (creds_identity,save_identity)))
 def directories():
  held_directory(credsfd,CREDS,creds_identity);held_directory(savefd,SAVE,save_identity)
  require(not os.listxattr(CREDS)and not os.listxattr(SAVE))
 def save(name,value):
  directories()
  with(SAVE/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
  os.fsync(savefd);directories()
 directories();before=snapshot(True);require(before==snapshot(True));save('before.private.json',before);save('dependencies-before.private.json',last_dependencies);print('REF_READY',flush=True)
 state='READY'
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii')
  require(owner()==held);directories()
  if action=='prepare':
   require(state=='READY'and snapshot(True)==before)
   synthetic={'bootstrap-admin-username':bytearray(b'pgpt_bootstrap_570_existing'),'bootstrap-admin-password':bytearray(secrets.token_urlsafe(32).encode('ascii'))}
   for name,value in sorted(synthetic.items()):
    directories()
    fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o400,dir_fd=credsfd)
    with os.fdopen(fd,'wb')as f:f.write(value);f.flush();os.fsync(f.fileno())
    require(strict(CREDS/name,0o400,256)==value);prepared[str(CREDS/name)]=tree(CREDS)[str(CREDS/name)]
   os.fsync(credsfd);directories();snapshot(True);state='PREPARED';print('REF_CHECKED',flush=True)
  elif action=='run':
   require(state=='PREPARED');connection(False);snapshot(False)
   save('start-reserved.private.json',{'unit':UNIT,'oneStart':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
   require(owner()==held);command(['/usr/bin/systemctl','start','--no-block',UNIT],4096)
   deadline=time.monotonic()+35;actor=None;inv=None;job=None;states=[]
   while time.monotonic()<deadline:
    observed=stable_actor('bootstrap',lambda role:show(UNIT,fields));states.append(observed)
    if observed.get('race'):time.sleep(.002);continue
    if observed['InvocationID']:
     if inv is None:inv=observed['InvocationID']
     require(inv==observed['InvocationID'])
    if observed['Job'].isdigit()and int(observed['Job'])>0:
     if job is None:job=observed['Job']
     require(job==observed['Job'])
    if int(observed['MainPID'])and observed.get('entry')==ENTRY and actor is None:
     p=pathlib.Path('/proc')/observed['MainPID']
     try:
      values={k:v.strip()for k,v in(x.split(':',1)for x in(p/'status').read_text().splitlines())}
      ticks=(p/'stat').read_text().rpartition(')')[2].split()[19]
      require(values['Uid'].split()==['999']*4 and values['Gid'].split()==['981']*4)
      groups=sorted(set(command(['/usr/bin/id','-G','schubert-api'],4096).decode().split()),key=int)
      require(sorted(set(values['Groups'].split()),key=int)==groups and values['NoNewPrivs']=='1')
      require(all(int(values[k],16)==0 for k in('CapInh','CapPrm','CapEff','CapBnd','CapAmb')))
      require((p/'cgroup').read_text()=='0::/system.slice/'+UNIT+'\n')
      require(show(UNIT,fields)['MainPID']==observed['MainPID']and show(UNIT,fields)['InvocationID']==inv)
      require((p/'stat').read_text().rpartition(')')[2].split()[19]==ticks)
      actor={'pid':observed['MainPID'],'ticks':ticks,'invocation':inv,'zeroCapabilities':True};save('actor.private.json',actor)
     except(FileNotFoundError,ProcessLookupError):pass
    if inv and observed['MainPID']==observed['ControlPID']=='0'and not observed['Job']and observed['ActiveState']in('inactive','failed'):break
    time.sleep(.002)
   save('states.private.json',states)
   require(actor is not None and job is not None and normal20(show(UNIT,fields)))
   terminal=show(UNIT,fields);require(terminal['InvocationID']==inv and not pathlib.Path('/proc',actor['pid']).exists());kernel(UNIT)
   require(fully_absent(pathlib.Path('/run/credentials',UNIT)))
   native_invocation=inv
   journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+inv,'-o','json','--no-pager'],4194304)
   messages=[json.loads(l).get('MESSAGE')for l in journal.splitlines()]
   require(messages.count('Initial ADMIN bootstrap finished')==messages.count('Bootstrap fixed PT native capture complete')==1 and 'Initial ADMIN bootstrap failed'not in messages)
   pid1=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+UNIT,'INVOCATION_ID='+inv,'-o','json','--no-pager'],4194304)
   records=[json.loads(l)for l in pid1.splitlines()]
   done=[r for r in records if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_ID')==job and r.get('JOB_RESULT')=='done'and r.get('JOB_TYPE')=='start']
   require(len(done)==1 and all(r.get('_PID')=='1'and r.get('_UID')=='0'and r.get('_COMM')=='systemd'and r.get('_BOOT_ID')==BOOT.replace('-','')for r in records))
   require(not any(r.get('JOB_RESULT')not in(None,'done')for r in records))
   with(SAVE/'journal.private.jsonl').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(journal);f.flush();os.fsync(f.fileno())
   with(SAVE/'pid1.private.jsonl').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(pid1);f.flush();os.fsync(f.fileno())
   snapshot(False);save('terminal.private.json',terminal);state='RAN';print('REF_CHECKED',flush=True)
  elif re.fullmatch('retire:[1-9][0-9]*',action):
   require(state=='RAN');backend=int(action.split(':')[1]);snapshot(True)
   for name,value in sorted(synthetic.items()):
    directories()
    require(strict(CREDS/name,0o400,256)==value)
    require(not(SAVE/(name+'.retired.private')).exists())
    retire_no_replace(credsfd,name,savefd)
    retired=SAVE/(name+'.retired.private')
    require(strict(retired,0o400,256)==value)
    require(metadata(retired)[:7]==prepared[str(CREDS/name)]['metadata'][:7])
    require(not os.path.lexists(CREDS/name))
   os.fsync(credsfd);os.fsync(savefd);directories();prepared.clear();post=snapshot(True);save('after.private.json',post)
   state='RETIRED';print('REF_CHECKED',flush=True)
  elif action=='release':
   require(state==('READY'if MODE=='verify'else'RETIRED'));post=snapshot(False)
   if MODE=='verify':save('after.private.json',post)
   for u in reversed(refs):manager.UnrefUnit(u)
   directories();bus.close();os.close(credsfd);os.close(savefd)
   for value in synthetic.values():value[:]=b'\0'*len(value)
   print('REF_RELEASED',flush=True);return
  else:raise ValueError('fixed existing bootstrap phase required')
 raise ValueError('bootstrap owner channel ended')
if __name__=='__main__':
 try:main()
 except Exception as failure:
  import traceback
  print('REF_FAILED',flush=True);print('PG570_READBACK_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG570_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
