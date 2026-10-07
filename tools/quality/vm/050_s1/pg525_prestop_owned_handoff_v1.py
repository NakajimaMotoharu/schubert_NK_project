"""SSC213 fixed PG524 operator-only handoff. Business four actors remain live and untouched."""
import ast,hashlib,json,os,pathlib,signal,stat,subprocess,time
PID=560210;TICKS=1926229;CHILD=560239;CHILD_TICKS=1926340
ARGV='9b1b8949c16b214dc83fb808e40d0ed3d67769de8eca0099da4fe1dc8360e1e1'
CHILD_ARGV='aae5a794feb3a901d89fb7ab7bc9127d19f7afc3da03bf2bf29355ad15a8b9c3'
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg524-native-tools-v1')
OLD=pathlib.Path('/var/lib/pgpt-s1-preservation/pg524-native-stop-v1')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg525-prestop-owned-handoff-v1')
PINS={'Pg524NativeStop.class':'7d17b597b84d13582953748bf77ea30057dc89ff836f329524eb0fd8810ed864','Pg524NativeStop$References.class':'d7148a782cefef668d37e698c7e60f1a70d260820c754712776d48633535a4b6','pg524_native_refs.py':'a9c2bb1e429db47e8e2a8983a39716ea8297031ea97a1386d3863834efa9e1c3','pg524_native_owned_stop.py':'612e29a5f689a3773ff9b84edaa21b546db3a7f091769027916730da8a573ad0','pg524_term_witness.py':'12b31d12c82c4c068a577e9ad1ef2bce3d5d23812d9b9242698c90681971c31d','pg524_native_term_witness.py':'398fc59422a4abea4acd06ef60566b745dca5effb329c0bb1f7fddd2ec759ade'}
LIVE={'artemis.service':(353417,1525015,'3808fe18268e42a09164a1bdc23e95c7'),'caddy.service':(512938,1620623,'bcb3353f526a4bd59a715cd4eb99d9fe'),'schubert-nk-api.service':(504968,1616183,'844d2217a6494e4f9f852fc4f488a0fa'),'schubert-nk-web.service':(507277,1617567,'7127bb06489a4218acd2b72570ce1ec5')}
def require(v):
 if not v:raise ValueError('fixed live-cohort pre-stop handoff refused')
def identity(value,pid,ticks,argv,parent=None):
 return(isinstance(value,dict)and set(value)=={'pid','ticks','argv','uid','parent','children'}and type(value['pid'])is int and value['pid']==pid and type(value['ticks'])is int and value['ticks']==ticks and value['argv']==argv and value['uid']==['0']*4 and type(value['parent'])is int and(parent is None or value['parent']==parent)and isinstance(value['children'],set)and all(type(c)is int and c>1 for c in value['children']))
def process(pid):
 p=pathlib.Path('/proc')/str(pid);s=(p/'stat').read_text().rpartition(')')[2].split()
 r={'pid':pid,'ticks':int(s[19]),'parent':int(s[1]),'argv':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'uid':(p/'status').read_text().split('Uid:')[1].splitlines()[0].split(),'children':{int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}}
 require(r['ticks']==int((p/'stat').read_text().rpartition(')')[2].split()[19]));return r
def owner(child):
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 r=process(PID);require(identity(r,PID,TICKS,ARGV)and r['children']==({CHILD}if child else set()))
 if child:
  c=process(CHILD);require(identity(c,CHILD,CHILD_TICKS,CHILD_ARGV,PID)and not c['children'])
 links=set()
 for fd in(pathlib.Path('/proc')/str(PID)/'fd').iterdir():
  try:links.add(str(fd.readlink()))
  except FileNotFoundError:pass
 for n,m in lock_baseline.items():
  p=pathlib.Path('/run/schubert-nk')/n;require(metadata(p)==m and str(p)in links);hits=[]
  for l in pathlib.Path('/proc/locks').read_text().splitlines():
   f=l.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if len(d)==3 and tuple(int(x,16)for x in d[:2])+(int(d[2]),)==(os.major(m[0]),os.minor(m[0]),m[1]):hits.append(l)
  require(len(hits)==1)
def peer_contract(peers,locks):
 if peers==[]and locks==[]:return True
 return(isinstance(peers,list)and len(peers)==1 and isinstance(locks,list)and len(locks)==1 and isinstance(peers[0],dict)and set(peers[0])=={'pid','application','user'}and type(peers[0]['pid'])is int and peers[0]['pid']>1 and peers[0]['application']=='PG524-native-stop'and peers[0]['user']=='schubert_batch'and locks[0]=={'pid':peers[0]['pid'],'mode':'ExclusiveLock'})
def cold_lock_reference(value):
 if not isinstance(value,dict) or set(value)!={'units','rows','trees','owner','prepared'} or value['prepared'] is not True:return False
 owner=value['owner']
 if not isinstance(owner,list) or len(owner)!=3 or type(owner[0]) is not int or owner[0]<2 or type(owner[1]) is not int or owner[1]<1:return False
 locks=owner[2]
 if not isinstance(locks,dict) or set(locks)!={'maintenance.lock','startup-admission.lock'}:return False
 for v in locks.values():
  if not isinstance(v,list) or len(v)!=9 or any(type(x) is not int or x<0 for x in v):return False
  if v[1]<1 or v[2:7]!=[0,0,stat.S_IFREG|0o600,1,0]:return False
 return isinstance(value['units'],dict) and len(value['units'])==10 and isinstance(value['rows'],dict) and len(value['rows'])==24 and isinstance(value['trees'],dict)
def peers_current():
 q="select coalesce(jsonb_agg(jsonb_build_object('pid',pid,'application',application_name,'user',usename)),'[]'::jsonb) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_backup');select coalesce(jsonb_agg(jsonb_build_object('pid',pid,'mode',mode)),'[]'::jsonb) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;"
 lines=command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==2);p,l=[json.loads(x)for x in lines];require(peer_contract(p,l));return {'peers':p,'locks':l}
def raw():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={u:show(u,FIELDS)for u in UNITS};require(units==baseline['units'])
 for u,v in units.items():
  if u in LIVE:
   pid,ticks,inv=LIVE[u];require(v['MainPID']==str(pid)and v['InvocationID']==inv and v['ActiveState']=='active'and v['SubState']=='running'and v['Job']==''and v['ControlPID']=='0')
   p=pathlib.Path('/proc')/str(pid);require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks and(p/'cgroup').read_text()=='0::/system.slice/'+u+'\n')
  else:
   require(v['MainPID']==v['ControlPID']=='0'and v['Job']=='')
 configuration={u:show(u,configuration_fields())for u in UNITS};require(configuration==baseline['configuration'])
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for t in baseline['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from(select to_jsonb(t)j from "+t+" t)q;"
 for l in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
  v=json.loads(l);require(v['table']not in rows);rows[v['table']]=v['rows']
 require(rows==baseline['rows']);startup=tree(pathlib.Path('/run/schubert-nk/startup'));originals=tree(pathlib.Path('/var/lib/schubert-nk/maintenance'));backup=tree(pathlib.Path('/srv/schubert-nk/backup'))
 require(startup==baseline['startup']and originals==baseline['originals']and backup==baseline['backup'])
 native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'));runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
 require(hashlib.sha256(runtime.read_bytes()).hexdigest()=='3992c3bcbe97066de238cb97678bb71537643bb598dd5b63a702b15d9e2e44e3')
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495');require(str(pathlib.Path('/opt/schubert-nk/current').readlink())==str(release)and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44')
 require('ro'in command(['/usr/bin/findmnt','--target',str(release),'--output','OPTIONS','--noheadings']).decode().strip().split(','))
 require(units=={u:show(u,FIELDS)for u in UNITS});peers_current()
 return{'units':units,'configuration':configuration,'rows':rows,'startup':startup,'originals':originals,'backup':backup,'native':native,'runtime':{'metadata':metadata(runtime),'sha256':hashlib.sha256(runtime.read_bytes()).hexdigest()}}
def save(n,v):
 with(SAVE/n).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def wait_gone(pid,seconds):
 end=time.monotonic()+seconds
 while pathlib.Path('/proc',str(pid)).exists()and time.monotonic()<end:time.sleep(.05)
 require(not pathlib.Path('/proc',str(pid)).exists())
def execute(perform=True):
 global baseline,lock_baseline
 require(os.geteuid()==0 and not SAVE.exists());os.umask(0o077)
 for n,digest in PINS.items():
  p=TOOLS/n;s=p.lstat();require(s.st_uid==s.st_gid==0 and s.st_mode==0o100400 and s.st_nlink==1 and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 witness=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(witness).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7');s=ast.parse(witness)
 names={'command','show','metadata','tree','configuration_fields'};definitions=[n for n in s.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names));constants=[n for n in s.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in{'UNITS','FIELDS'}for t in n.targets)]
 exec(compile(ast.Module(body=constants+definitions,type_ignores=[]),'<fixed readonly definitions>','exec'),globals())
 require({p.name for p in OLD.iterdir()}=={'refs-prepare.private.log','before.private.json'})
 b=(OLD/'before.private.json').read_bytes();require(hashlib.sha256(b).hexdigest()=='15fa5248869a1290940d776cf9886213475d4ff8850a5b13ad34e75ede5d32eb');baseline=json.loads(b)
 require(set(baseline)=={'units','configuration','rows','pid1','startup','originals','backup'}and len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==462)
 require(hashlib.sha256((OLD/'refs-prepare.private.log').read_bytes()).hexdigest()=='add3b29f88babf96990f1a2af77b1af299cfa052be658fa3f816fead5997fe6e')
 lock_reference=pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-preparation-v1/refs-after.private.json').read_bytes();require(hashlib.sha256(lock_reference).hexdigest()=='07d74f8b4a5dbf99b801ff2f272e57d1e693dfba61d323800dc180fc6b6d2f49');lock_value=json.loads(lock_reference);require(cold_lock_reference(lock_value));lock_baseline=lock_value['owner'][2]
 owner(True);value=raw();owner(True);require(value==raw());owner(True)
 require(type(perform)is bool)
 if not perform:
  print('PG525_PREFLIGHT fullRawUnchangedTwice=true currentOwner=true businessActions0=true');return
 parent_fd=os.pidfd_open(PID);child_fd=os.pidfd_open(CHILD);owner(True)
 SAVE.mkdir(mode=0o700);save('before.private.json',value);save('peer-before.private.json',peers_current());save('old-ref-error.private.json',{'sha256':hashlib.sha256((OLD/'refs-prepare.private.log').read_bytes()).hexdigest(),'oldCloseUNKNOWN':True})
 require(value==raw());owner(True);save('term-reservation.private.json',{'pid':PID,'ticks':TICKS,'argv':ARGV,'child':CHILD,'childTicks':CHILD_TICKS,'childArgv':CHILD_ARGV,'boot':BOOT,'repeatForbidden':True,'businessStop0':True,'oldCloseUNKNOWN':True})
 owner(True);signal.pidfd_send_signal(child_fd,signal.SIGTERM);os.close(child_fd);wait_gone(CHILD,5)
 owner(False);signal.pidfd_send_signal(parent_fd,signal.SIGTERM);os.close(parent_fd);wait_gone(PID,15)
 require(value==raw()and value==raw());require(peers_current()=={'peers':[],'locks':[]})
 for m in lock_baseline.values():
  for l in pathlib.Path('/proc/locks').read_text().splitlines():
   f=l.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
 save('complete.private.json',{'ownedChildThenJavaTERM':True,'allRawUnchangedTwice':True,'liveCohortPreserved':True,'ownPeerLocks0':True,'oldCloseUNKNOWN':True,'businessActions0':True})
 print('PG525_PRESTOP_OWNED_HANDOFF ownedTERM=true liveCohortPreserved=true fullRawUnchangedTwice=true ownPeerLocks0=true oldCloseUNKNOWN=true')
if __name__=='__main__':execute()
