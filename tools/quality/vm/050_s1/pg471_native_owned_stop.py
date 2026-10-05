"""SSC190191 current normal-DONE cohort stop only, under enclosing Java M/A/DB.
Full captures/terminal receipts remain Root-private. No start/repair/permit/DDL.
"""
import hashlib,json,os,pathlib,stat,subprocess,sys
from pg466_term_witness import FIELDS,unique
from pg471_native_term_witness import witness
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg471-native-stop-v1')
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
ORDER=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']
EXPECTED={'caddy.service':('2273164','d3f960c22ef2455386519d18146139a8'),
 'schubert-nk-web.service':('2267460','a0e695e907204a7eaf84ae16013493ad'),
 'schubert-nk-api.service':('2265107','8d6e47b48a58468aaac34643bbeddb16'),
 'artemis.service':('2145457','3e037033f5cd4cbd8ce1c9f8160f1238')}
def require(value):
 if not value:raise ValueError('current owned stop refused')
def validate_live(captures):
 require(isinstance(captures,dict) and set(captures)==set(ORDER))
 for unit,pair in EXPECTED.items():
  b=captures[unit];require(isinstance(b,dict) and set(b)==FIELDS and all(isinstance(v,str) for v in b.values()))
  require((b['MainPID'],b['InvocationID'])==pair and b['ActiveState']=='active' and b['SubState']=='running'
   and b['Job']=='' and b['ControlPID']=='0' and b['Result']=='success' and b['Id']==unit and b['LoadState']=='loaded'
   and b['ExecMainCode']==b['ExecMainStatus']==b['ExecMainExitTimestampMonotonic']=='0')
def command(args,timeout=5):
 r=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=timeout)
 require(r.returncode==0 and len(r.stdout)<=4194304);return r.stdout
def show(unit):
 require(unit in ORDER);v={}
 for line in command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode('ascii').splitlines():
  k,value=line.split('=',1);require(k not in v);v[k]=value
 require(set(v)==FIELDS and v['Id']==unit and v['LoadState']=='loaded');return v
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def holder():
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);argv=(p/'cmdline').read_bytes().split(b'\0')
 require(argv[-3:]==[b'Pg471NativeStop',b'stop',b''] and argv[0]==b'/opt/jdk-25.0.4/bin/java')
 fds=[]
 for fd in (p/'fd').iterdir():
  try:fds.append(str(fd.readlink()))
  except FileNotFoundError:continue
 for name in ('maintenance.lock','startup-admission.lock'):
  target=pathlib.Path('/run/schubert-nk')/name;st=target.stat()
  require(st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1 and str(target) in fds)
  matches=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    dev=f[5].split(':')
    if len(dev)==3 and (int(dev[0],16),int(dev[1],16),int(dev[2]))==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):matches.append(line)
  require(len(matches)==1)
 return (pid,tick(pid))
def kernel_empty(unit):
 c=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
 if c.exists():
  for p in [c,*[x for x in c.rglob('*') if x.is_dir()]]:
   require(not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text())
def terminal(v):return v['MainPID']==v['ControlPID']=='0' and v['Job']=='' and v['ActiveState'] in ('inactive','failed')
def same_generation(before,after):
 return all(before[k]==after[k] for k in ('Id','LoadState','InvocationID','ExecMainStartTimestampMonotonic','Type','Restart','RemainAfterExit','KillMode','SendSIGKILL'))
def normal_terminal(before,after):
 if not isinstance(before,dict) or not isinstance(after,dict) or set(before)!=FIELDS or set(after)!=FIELDS or not all(isinstance(v,str) for v in (*before.values(),*after.values())):return False
 if before['Id'] not in ('caddy.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service') or before['LoadState']!='loaded' or not same_generation(before,after):return False
 if not terminal(after) or after['ActiveState']!='inactive' or after['SubState']!='dead' or after['Result']!='success':return False
 if before['Result']!='success' or before['ControlPID']!='0' or before['Job']!='' or not before['MainPID'].isdigit():return False
 if before['MainPID']=='0':return after['ExecMainCode']==before['ExecMainCode'] and after['ExecMainStatus']==before['ExecMainStatus'] and after['ExecMainExitTimestampMonotonic']==before['ExecMainExitTimestampMonotonic']
 return before['ActiveState']=='active' and before['SubState']=='running' and before['ExecMainCode']==before['ExecMainStatus']==before['ExecMainExitTimestampMonotonic']=='0' and after['ExecMainCode']=='1' and after['ExecMainStatus']=='0' and before['ExecMainStartTimestampMonotonic'].isdigit() and after['ExecMainExitTimestampMonotonic'].isdigit() and 0<int(before['ExecMainStartTimestampMonotonic'])<=int(after['ExecMainExitTimestampMonotonic'])
def broker_witness(before,after,raw):
 require(isinstance(before,dict) and isinstance(after,dict) and set(before)==set(after)==FIELDS and all(isinstance(v,str) for v in (*before.values(),*after.values())))
 require(before['Id']=='artemis.service' and before['LoadState']=='loaded' and before['ActiveState']=='active' and before['SubState']=='running' and before['Result']=='success' and before['MainPID'].isdigit() and int(before['MainPID'])>0 and before['ControlPID']=='0' and before['Job']=='')
 require(before['ExecMainCode']==before['ExecMainStatus']==before['ExecMainExitTimestampMonotonic']=='0')
 require(same_generation(before,after) and terminal(after) and after['ActiveState']=='inactive' and after['SubState']=='dead' and after['Result']=='success' and after['ExecMainCode']=='1' and after['ExecMainStatus']=='143')
 require(before['ExecMainStartTimestampMonotonic'].isdigit() and after['ExecMainExitTimestampMonotonic'].isdigit() and 0<int(before['ExecMainStartTimestampMonotonic'])<=int(after['ExecMainExitTimestampMonotonic']))
 require(isinstance(raw,bytes) and 0<len(raw)<=4194304 and raw.endswith(b'\n'))
 cursors=set();stopped=0
 for line in raw.decode('utf-8',errors='strict').splitlines():
  r=json.loads(line,object_pairs_hook=unique)
  for k in ('__CURSOR','__MONOTONIC_TIMESTAMP','__REALTIME_TIMESTAMP','_BOOT_ID','_SYSTEMD_UNIT','_SYSTEMD_INVOCATION_ID','PRIORITY','MESSAGE'):require(isinstance(r.get(k),str))
  require(r['_BOOT_ID']==BOOT.replace('-','') and r['_SYSTEMD_UNIT']=='artemis.service' and r['_SYSTEMD_INVOCATION_ID']==before['InvocationID'])
  require(r['PRIORITY'] in ('4','5','6','7') and r['__CURSOR'] and r['__CURSOR'] not in cursors);cursors.add(r['__CURSOR'])
  require(r['__MONOTONIC_TIMESTAMP'].isdigit() and r['__REALTIME_TIMESTAMP'].isdigit() and int(before['ExecMainStartTimestampMonotonic'])<=int(r['__MONOTONIC_TIMESTAMP'])<=int(after['ExecMainExitTimestampMonotonic']))
  require('AMQ224' not in r['MESSAGE'] and not any(x in r['MESSAGE'].split() for x in ('ERROR','FATAL')))
  if 'AMQ221002: Apache Artemis Message Broker version 2.56.0' in r['MESSAGE'] and ' stopped, uptime ' in r['MESSAGE']:stopped+=1
 require(stopped==1);return {'rows':len(cursors),'sha256':hashlib.sha256(raw).hexdigest(),'vendorStopData':True,'unitExit143IsStopData':True}
def save(name,data):
 with (ROOT/name).open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
def stop_one(unit,captures,ticks):
 require(unit in ORDER and set(captures)==set(ORDER))
 index=ORDER.index(unit)
 require(all((ROOT/(prior+'.stopped.private')).is_file() for prior in ORDER[:index]))
 owner=holder();before=captures[unit];current=show(unit);issued=False
 if current==before and not terminal(current):
  if before['MainPID']!='0':require(tick(before['MainPID'])==ticks[unit] and (pathlib.Path('/proc')/before['MainPID']/'cgroup').read_text()=='0::/system.slice/'+unit+'\n')
  require(holder()==owner);save(unit+'.stop-reserved.private',b'oneOwnedStop=true\n')
  r=subprocess.run(['/usr/bin/systemctl','stop',unit],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120);require(r.returncode==0);issued=True
  current=show(unit)
 else:
  # Dependency termination is authenticated, never blindly reissued.
  require(terminal(current) and same_generation(before,current))
 require(terminal(current) and same_generation(before,current));kernel_empty(unit)
 if before['MainPID']!='0':require(not (pathlib.Path('/proc')/before['MainPID']).exists())
 if unit in ('schubert-nk-api.service','schubert-nk-web.service','artemis.service'):
  raw=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+before['InvocationID'],'-o','json','--no-pager']);save(unit+'.full-journal.private.jsonl',raw)
  data=broker_witness(before,current,raw) if unit=='artemis.service' else witness('API' if 'api' in unit else 'WEB',before,current,raw,before['MainPID'],'999' if 'api' in unit else '997')
  save(unit+'.stop-witness.private',json.dumps(data,sort_keys=True).encode())
 else:
  require(normal_terminal(before,current))
 require(current==show(unit) and holder()==owner);save(unit+'.stopped.private',json.dumps(current,sort_keys=True).encode())
 print('PG471_NATIVE_OWNED_STOP unit='+unit+' explicit='+str(issued).lower()+' sameGeneration=true kernelEmpty=true starts0=true',flush=True)
def main():
 require(os.geteuid()==0 and len(sys.argv)==2 and sys.argv[1] in [*ORDER,'capture'] and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG471'))
 for target in ('timers.target','paths.target'):
  require(command(['/usr/bin/systemctl','show',target,'--property=LoadState']).strip()==b'LoadState=masked')
 require(stat.S_IMODE(ROOT.stat().st_mode)==0o700 and ROOT.stat().st_uid==0)
 if sys.argv[1]=='capture':
  owner=holder();captures={unit:show(unit) for unit in ORDER};ticks={}
  validate_live(captures)
  for unit,b in captures.items():
   if b['MainPID']!='0':
    ticks[unit]=tick(b['MainPID']);require((pathlib.Path('/proc')/b['MainPID']/'cgroup').read_text()=='0::/system.slice/'+unit+'\n')
   require(b==show(unit) and owner==holder())
  save('stops-before.private',json.dumps(captures,sort_keys=True).encode());save('ticks-before.private',json.dumps(ticks,sort_keys=True).encode())
  fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:os.fsync(fd)
  finally:os.close(fd)
  print('PG471_NATIVE_CAPTURE sameCohort=true heldMA=true starts0=true');return
 captures=json.loads((ROOT/'stops-before.private').read_text(),object_pairs_hook=unique)
 ticks=json.loads((ROOT/'ticks-before.private').read_text(),object_pairs_hook=unique)
 stop_one(sys.argv[1],captures,ticks)
if __name__=='__main__':main()
