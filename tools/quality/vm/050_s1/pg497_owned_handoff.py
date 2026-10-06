"""SSC205: fixed PG496 revoke-before UNKNOWN owner only; one pidfd TERM.
No ordinary Unit operation, start, database write, epoch or old-close normalization.
All full records remain Root-private. Import is free of runtime actions.
"""
import ast,hashlib,json,os,pathlib,re,signal,stat,subprocess,sys,time
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
PID=19311;TICKS=26219552
ARGV='36f1c62fe368414aea656a9173414708e3bb65f8dc1cd835c2f21de0523dfc12'
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6')
OLD=pathlib.Path('/var/lib/pgpt-s1-preservation/pg496-timeout-no-intents-v1')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg497-owned-tool-handoff-v1')
def require(value):
 if not value:raise ValueError('fixed pending tool handoff refused')
def owner_shape(boot,pid,ticks,argv,uid,children):
 return boot=='e07aa706-1acd-4e65-b309-d7f330f79d54' and pid==19311 and ticks==26219552 and argv=='36f1c62fe368414aea656a9173414708e3bb65f8dc1cd835c2f21de0523dfc12' and uid==['0','0','0','0'] and children==set()
def peer_shape(peers,locks,after):
 if not isinstance(peers,list) or not isinstance(locks,list):return False
 if after:return peers==locks==[]
 if len(peers)>2 or len(locks)>1:return False
 for p in peers:
  if not isinstance(p,dict) or p.get('usename') not in ['schubert_batch','schubert_migration'] or p.get('application_name')!=('PG496-fixed-recovery' if p.get('usename')=='schubert_batch' else 'PG496-fixed-snapshot') or type(p.get('pid')) is not int or not 0<p['pid']<=4294967295:return False
 if len({p['usename'] for p in peers})!=len(peers):return False
 batch=[p for p in peers if p['usename']=='schubert_batch']
 return len(batch)<=1 and (locks==[] if not batch else locks==[{'pid':batch[0]['pid'],'mode':'ExclusiveLock'}])
def owner():
 p=pathlib.Path('/proc')/str(PID);argv=(p/'cmdline').read_bytes();children=set()
 for task in (p/'task').iterdir():children.update((task/'children').read_text().split())
 status={k:v.split() for k,v in (line.split(':',1) for line in (p/'status').read_text().splitlines() if ':' in line)}
 ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19])
 require(owner_shape(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),PID,ticks,hashlib.sha256(argv).hexdigest(),status['Uid'],children))
 require(status['Gid']==['0']*4 and argv.split(b'\0')[0]==b'/opt/jdk-25.0.4/bin/java' and argv.split(b'\0')[-3:]==[b'Pg496TimeoutRecovery',b'recover',b''])
 links=[]
 for fd in (p/'fd').iterdir():
  try:links.append(str(fd.readlink()))
  except FileNotFoundError:continue
 for name in ['maintenance.lock','startup-admission.lock']:
  target=pathlib.Path('/run/schubert-nk')/name;s=target.lstat()
  require(stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==s.st_gid==0 and s.st_nlink==1 and str(target) in links and 'system.posix_acl_access' not in os.listxattr(target))
  matches=[]
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    dev=f[5].split(':')
    if len(dev)==3 and (int(dev[0],16),int(dev[1],16),int(dev[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matches.append(row)
  require(len(matches)==1)
 return {'pid':PID,'ticks':ticks,'argvSha256':ARGV,'bothMAHeld':True,'allTaskChildren':0}
def peers(after):
 sql="select json_build_object('peers',coalesce((select jsonb_agg(jsonb_build_object('pid',pid,'usename',usename,'application_name',application_name) order by pid) from pg_catalog.pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_backup','schubert_inbox_inspector','schubert_web_session','schubert_migration','schubert_ops_ro')),'[]'::jsonb),'locks',coalesce((select jsonb_agg(jsonb_build_object('pid',pid,'mode',mode) order by pid) from pg_catalog.pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted),'[]'::jsonb))"
 value=json.loads(h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]));require(peer_shape(value['peers'],value['locks'],after))
 # Current fixed case has independently observed expiry/0. Do not admit any live or foreign DB by alias.
 require(value['peers']==value['locks']==[]);return value
def no_ma_holders():
 for name in ['maintenance.lock','startup-admission.lock']:
  s=(pathlib.Path('/run/schubert-nk')/name).lstat()
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1:4]==['FLOCK','ADVISORY','WRITE']:
    d=f[5].split(':')
    require(len(d)!=3 or (int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
def same_configuration(before,after,old,current,ended):
 if not isinstance(before,dict) or not isinstance(after,dict) or set(before)!=set(after) or 'ExecStart' not in before:return False
 if any(before[k]!=after[k] for k in before if k!='ExecStart'):return False
 if before['ExecStart']==after['ExecStart']:return True
 a=exec_record(before['ExecStart']);b=exec_record(after['ExecStart'])
 return a is not None and b is not None and a[:4]==b[:4] and b[4]==ended and b[4]!='n/a' and a[5]==b[5]==old.get('MainPID') and b[6]=='exited' and current.get('ExecMainCode')=='1' and b[7]==current.get('ExecMainStatus') and w.same_generation(old,current)
def unchanged():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG489'))
 before=json.loads((OLD/'snapshot-before.private.json').read_text());actual=h.snapshot()
 require(before['rows']==actual['rows'] and before['trees']==actual['trees'] and set(before['configuration'])==set(actual['configuration']))
 require(h.epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),False))
 units={u:h.show(u) for u in h.ORDER+h.EXTRA};old=json.loads((OLD/'units-before.private.json').read_text())
 for u,v in units.items():
  require(v['MainPID']==v['ControlPID']=='0' and v['Job']=='');h.kernel_empty(u)
  if u in h.ORDER[:-1]:require(v==json.loads((OLD/(u+'.stopped.private')).read_text()))
  elif u=='artemis.service':require(w.same_generation(old[u],v))
  else:require(v==old[u])
  if before['configuration'][u]!=actual['configuration'][u]:
   ended=h.command(['/usr/bin/systemctl','show',u,'--property=ExecMainExitTimestamp']).decode('ascii').strip().removeprefix('ExecMainExitTimestamp=')
   require(same_configuration(before['configuration'][u],actual['configuration'][u],old[u],v,ended))
 require(units=={u:h.show(u) for u in units});return units
def save(name,data):
 with (SAVE/name).open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def main():
 global h,w,exec_record
 require(os.geteuid()==0 and len(sys.argv)==2 and sys.argv[1]=='handoff' and not SAVE.exists())
 require(hashlib.sha256((TOOLS/'payload-sha256.json').read_bytes()).hexdigest()=='eadeeb0d78415e6fb6affedd5383f44f3aa4bce1fd031bc49602d9cac602874b')
 for name,digest in json.loads((TOOLS/'payload-sha256.json').read_text()).items():
  p=TOOLS/name;s=p.lstat();require(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 sys.path.insert(0,str(TOOLS));import pg496_timeout_owned as helper;import pg481_native_owned_stop as witness
 h=helper;w=witness;h.load_definitions()
 parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
 require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 definitions=[n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record'];require(len(definitions)==1)
 exec(compile(ast.Module(body=definitions,type_ignores=[]),'<pinned complete ExecStart parser>','exec'),globals())
 fixed=owner();db=peers(False);units=unchanged();require(owner()==fixed and unchanged()==units)
 before=json.loads((OLD/'units-before.private.json').read_text())['artemis.service']
 raw=h.command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+before['InvocationID'],'-o','json','--no-pager'])
 stopped=w.broker_witness(before,units['artemis.service'],raw)
 pid1=h.command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT=artemis.service','-o','json','--no-pager'])
 records=[json.loads(x) for x in pid1.splitlines()];done=[r for r in records if r.get('INVOCATION_ID')=='12360e619aa7445684692c59badc7c51' and r.get('JOB_ID')=='309955' and r.get('JOB_TYPE')=='stop' and r.get('JOB_RESULT')=='done']
 require(len(done)==1 and done[0].get('_UID')=='0' and done[0].get('_PID')=='1' and done[0].get('_COMM')=='systemd' and done[0].get('_BOOT_ID')==BOOT.replace('-','') and done[0].get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'
  and 262205737378<=int(done[0]['__MONOTONIC_TIMESTAMP'])<=262205899571)
 SAVE.mkdir(mode=0o700);save('broker-full-journal.private.jsonl',raw);save('broker-pid1.private.jsonl',pid1)
 save('before.private.json',json.dumps({'owner':fixed,'db':db,'units':units,'brokerWitness':stopped},sort_keys=True).encode())
 fd=os.pidfd_open(PID,0)
 try:
  require(owner()==fixed and unchanged()==units);peers(False)
  save('term-reserved.private.json',json.dumps({'pid':19311,'ticks':26219552,'onePidfdTerm':True,'oldCloseNotInferred':True}).encode())
  require(owner()==fixed);signal.pidfd_send_signal(fd,signal.SIGTERM)
  deadline=time.monotonic()+15
  while pathlib.Path('/proc/'+str(PID)).exists() and time.monotonic()<deadline:time.sleep(.05)
  require(not pathlib.Path('/proc/'+str(PID)).exists())
 finally:os.close(fd)
 peers(True);no_ma_holders();require(unchanged()==units);peers(True);no_ma_holders();require(unchanged()==units)
 save('complete.private.json',json.dumps({'ownedTerm':True,'allOldPeersLocksGone':True,'allTenKernelEmpty':True,'all24RowsAndOriginalValuesUnchanged':True,'source':'38899a05b5c2daeecfc5af8ea5ae748e29954c60','oldCloseNotInferred':True,'currentStillIssued':True,'starts':0,'revoke':0},sort_keys=True).encode())
 print('PG497_HANDOFF actualNormalOperatorReturn=true oldToolAbnormal=true oldCloseNotInferred=true allOriginalValuesUnchanged=true starts0=true revoke0=true')
if __name__=='__main__':main()
