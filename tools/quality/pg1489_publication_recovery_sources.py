"""SSC266 current failed-publication owner scope, ordinary reverse stops, typed retire.

Candidate generator only: no VM action. Primitive is independently qualified
PG1488; full owner/post/native acceptance remains a separate required gate.
"""
import ast
from pg1478_partial_original_profile_sources import java as profile_java,refs as profile_refs
from pg1334_published_owned_stop_sources_v2 import sources as stopped_sources

SAVE='pg1492-publication-only-recovery-v1'
TOOLS='pg1489-publication-only-tools-v1'
ORDER=('schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-cleanup.service')

def java():
    raw=profile_java()
    for old,new in [('Pg1478PartialOriginalProfile','Pg1489PublicationOnlyRecovery'),('pg1478-partial-original-tools-v1',TOOLS),('pg1481-partial-original-profile-v1',SAVE),('pg1478_partial_original_refs.py','pg1489_publication_recovery_refs.py'),('PG1481_','PG1492_'),('PG266-readonly-profile','PG266-publication-recover'),('"profile".equals(args[0])','"recover".equals(args[0])')]:
        if old not in raw:raise ValueError('one current profile binding required')
        raw=raw.replace(old,new)
    old='Set.of("prepare","prepared","run").contains(name)'
    assert raw.count(old)==1
    raw=raw.replace(old,'Set.of("prepare","prepared","run","stop-expiry","stop-artemis","stop-cleanup","retire-proof","retired").contains(name)')
    marker='              refs.check("prepared");original(session);'
    assert raw.count(marker)==1
    raw=raw.replace(marker,RECOVERY)
    raw=raw.replace('"allScopesReturnedNormally=true\\nreadonlyProfile=true\\nepochDbBusinessWrites=0\\n"','"allScopesReturnedNormally=true\\npublicationOnlyRecovered=true\\nepochDbBusinessWrites=0\\n"')
    raw=raw.replace('readonlyProfile=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false','publicationOnlyRecovered=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false')
    marker='  static final class References {'
    assert raw.count(marker)==1
    raw=raw.replace(marker,GUARD+'\n'+marker)
    return raw

GUARD=r'''
  static void recoveryGuard(References refs,MaintenanceRunFiles.Session session)throws IOException {
    try {original(session);refs.check("retire-proof");}
    catch(IOException failure){throw failure;}
    catch(Exception failure){throw new IOException("current owned recovery proof unavailable",failure);}
  }
'''

RECOVERY=r'''
              refs.check("prepared");original(session);
              for(String action:List.of("stop-expiry","stop-artemis","stop-cleanup")) {
                phase="CURRENT_OWNED_"+action;original(session);refs.check(action);original(session);
              }
              phase="TYPED_PUBLICATION_INTENT_RETIRE";
              try(var startup=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))) {
                var permits=new StartupPermitFiles(startup,LinuxInodeSecurity.create());
                var invalid=permits.current();
                require(invalid.state()==StartupPermitRecords.State.INVALID
                    && invalid.boot().toString().equals(BOOT)&&invalid.activation().equals(ORIGINAL)
                    &&invalid.epoch().toString().equals("b6e5cc96-3279-4cb8-a7f5-6584a3ac62c4"));
                dev.codex.schubert.nk.batch.file.Pg1487PublicationOnlyIntent.retire(startup,invalid,ORIGINAL,
                    "ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99",
                    "47be234990bd4aec838648a8f365536f",
                    ()->recoveryGuard(refs,session),()->recoveryGuard(refs,session));
                require(invalid.equals(permits.current()));refs.check("retired");original(session);
              }
'''

def refs():
    raw=profile_refs()
    for old,new in [('Pg1478PartialOriginalProfile','Pg1489PublicationOnlyRecovery'),("b'profile'","b'recover'"),('pg1481-partial-original-profile-v1',SAVE),('PG266-readonly-profile','PG266-publication-recover')]:
        if old not in raw:raise ValueError('current owner reference binding required')
        raw=raw.replace(old,new)
    # Keep the existing full snapshot readback but handle only authenticated stopped
    # stages. Each delta is qualified separately before normalization below.
    t=ast.parse(raw);snapshot=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    source=ast.unparse(snapshot)
    begin=source.index("    broker = units['artemis.service']")
    end=source.index('    durable =',begin)
    active=source[begin:end]
    source=source[:begin]+"    if 'artemis.service'not in STOPPED:\n"+'\n'.join('    '+line for line in active.splitlines())+"\n    else:\n        require(not pathlib.Path('/proc/41805').exists())\n        actor=None\n"+source[end:]
    begin=source.index('    observations = {}');end=source.index("    startup = runtime['startup']",begin)
    source=source[:begin]+"    observations=cohort_observations(units)\n"+source[end:]
    old="require(set(startup) == {rootPath, rootPath + '/epoch.current', rootPath + '/b6e5cc96-3279-4cb8-a7f5-6584a3ac62c4.permit', rootPath + '/permit-start.intent'})"
    assert source.count(old)==1
    source=source.replace(old,"require(set(startup)in [{rootPath,rootPath+'/epoch.current',rootPath+'/b6e5cc96-3279-4cb8-a7f5-6584a3ac62c4.permit',rootPath+'/permit-start.intent'},{rootPath,rootPath+'/epoch.current',rootPath+'/b6e5cc96-3279-4cb8-a7f5-6584a3ac62c4.permit'}])")
    begin=raw.index('def snapshot():');end=raw.index('expected_raw=',begin)
    witness=ast.parse(stopped_sources()['pg1334_native_owned_stop.py'])
    selected=[n for n in witness.body if isinstance(n,ast.FunctionDef)and n.name in {'broker_witness','same_generation','terminal'}]
    assert len(selected)==3
    pure=ast.unparse(ast.Module(body=selected,type_ignores=[]))
    raw=raw[:begin]+source+'\n'+pure+'\n'+HELPERS+'\n'+raw[end:]
    marker="require(status['Uid'].split() == status['Gid'].split() == ['0'] * 4"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19]);age=time.clock_gettime(time.CLOCK_MONOTONIC)-ticks/os.sysconf('SC_CLK_TCK');require(0<=age<1800)\n    "+marker)
    raw=raw.replace("value=snapshot();require(value==expected_current and value==snapshot());peer_check();inventory_check();return value","value=snapshot();validate_current(value);require(value==snapshot());peer_check();inventory_check();kernel_scope();return value")
    old="action=line.strip();require(action in {'prepare','prepared','run','release'})"
    assert raw.count(old)==1
    raw=raw.replace(old,"action=line.strip();require(action in {'prepare','prepared','run','release','stop-expiry','stop-artemis','stop-cleanup','retire-proof','retired'})\n  if action.startswith('stop-'):stop_one(action)\n  if action=='retired':RETIRED=True")
    raw=raw.replace("if action=='run':PEER_CLOSED=True","if action=='run':\n   require(tuple(STOPPED)==ORDER and RETIRED);PEER_CLOSED=True")
    raw=raw.replace("'mutation0':True","'onlyTypedIntentRetirement':True,'originalDbEpochPreserved':True")
    raw=raw.replace('import os, pathlib, stat, subprocess, json, hashlib, re, datetime','import os, pathlib, stat, subprocess, json, hashlib, re')
    raw=raw.replace('import dbus\nimport dbus, time, sys, types','import dbus, time, sys, types')
    compile(raw,'<candidate typed publication recovery refs>','exec');return raw

# Defined before snapshot's first invocation. No business mutation at import time.
HELPERS=r'''
ORDER=('schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-cleanup.service')
STOPPED=[];STOP_RECEIPTS={};RETIRED=False;BROKER_LOCKS=None

def unique(pairs):
 result={}
 for key,value in pairs:require(key not in result);result[key]=value
 return result

def kernel_empty(unit):
 path=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
 if path.exists():
  for child in [path,*[p for p in path.rglob('*')if p.is_dir()]]:
   require(not(child/'cgroup.procs').read_text().strip()and 'populated 0\n'in(child/'cgroup.events').read_text())

def kernel_scope():
 global BROKER_LOCKS
 for unit in UNITS:
  if unit=='artemis.service'and unit not in STOPPED:
   p=pathlib.Path('/proc/41805');s=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
   require(s['Uid'].split()==['994']*4 and s['Gid'].split()==['979']*4 and(p/'cgroup').read_text()=='0::/system.slice/artemis.service\n')
   group=pathlib.Path('/sys/fs/cgroup/system.slice/artemis.service')
   require((group/'cgroup.procs').read_text().split()==['41805'])
   require(all(not(path/'cgroup.procs').read_text().strip()for path in group.rglob('*')if path.is_dir()))
   require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==636663)
   require(not {int(child)for task in(p/'task').iterdir()for child in(task/'children').read_text().split()})
   found=[]
   for line in pathlib.Path('/proc/locks').read_text().splitlines():
    fields=line.split()
    if len(fields)==8 and fields[4]=='41805':
     require(fields[1]in {'FLOCK','POSIX'}and fields[2:4]==['ADVISORY','WRITE'])
     device=fields[5].split(':');require(len(device)==3)
     key=(int(device[0],16),int(device[1],16),int(device[2]))
     matches=[]
     for fd in(p/'fd').iterdir():
      try:st=fd.stat()
      except FileNotFoundError:continue
      if(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)==key:matches.append(fd)
     require(matches);found.append((fields[1],key))
   require(len(found)==3 and len(set(found))==3)
   if BROKER_LOCKS is None:BROKER_LOCKS=sorted(found)
   require(sorted(found)==BROKER_LOCKS)
  else:
   kernel_empty(unit)
   if unit=='artemis.service':
    require(BROKER_LOCKS is not None and not pathlib.Path('/proc/41805').exists())
    for line in pathlib.Path('/proc/locks').read_text().splitlines():
     fields=line.split()
     if len(fields)==8 and fields[1]in {'FLOCK','POSIX','OFDLCK'}:
      dev=fields[5].split(':');require(len(dev)==3)
      key=(int(dev[0],16),int(dev[1],16),int(dev[2]));require(key not in [v[1]for v in BROKER_LOCKS])

def cohort_observations(units):
 result={}
 for unit in ORDER:
  expected=expected_current['pid1CohortObservations'][unit]
  raw=command(['journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+unit,'INVOCATION_ID='+expected['invocation'],'-o','json','--no-pager'],1048576)
  records=[json.loads(line,object_pairs_hook=unique)for line in raw.splitlines()]
  if unit not in STOPPED:require(records==expected['pid1']);result[unit]=expected
  else:
   receipt=STOP_RECEIPTS[unit];require(records==receipt['pid1']);result[unit]=receipt
 return result

def validate_current(value):
 import copy
 actual=copy.deepcopy(value);expected=expected_current
 require(tuple(STOPPED)==ORDER[:len(STOPPED)])
 for unit in STOPPED:
  receipt=STOP_RECEIPTS[unit];require(actual['units'][unit]==receipt['after'])
  before=expected['configuration'][unit];after=actual['configuration'][unit]
  if after!=before:
   require(unit=='artemis.service'and set(before)==set(after))
   for key in before:
    if key!='ExecStart':require(before[key]==after[key])
   a=exec_record(before['ExecStart']);b=exec_record(after['ExecStart'])
   require(a is not None and b is not None and a[:4]==b[:4]and a[5]==b[5]=='41805'and b[6]=='exited'and b[7]=='143'and b[4])
  actual['configuration'][unit]=copy.deepcopy(before);actual['units'][unit]=copy.deepcopy(expected['units'][unit]);actual['pid1CohortObservations'][unit]=copy.deepcopy(expected['pid1CohortObservations'][unit])
 if 'artemis.service'in STOPPED:require(actual['brokerActor']is None);actual['brokerActor']=copy.deepcopy(expected['brokerActor'])
 tree0=expected['runtime']['startup'];tree1=actual['runtime']['startup'];root='/run/schubert-nk/startup';marker=root+'/permit-start.intent'
 if marker not in tree1:
  require(tuple(STOPPED)==ORDER and set(tree1)==set(tree0)-{marker})
  require(tree1[root]['sha256']is None and tree1[root]['metadata'][:6]==tree0[root]['metadata'][:6])
  for name in set(tree1)-{root}:require(tree1[name]==tree0[name])
  actual['runtime']['startup']=copy.deepcopy(tree0)
 else:require(not RETIRED)
 require(actual==expected)

def save(name,body):
 with(SAVE/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(body);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)

def stop_one(action):
 names={'stop-expiry':ORDER[0],'stop-artemis':ORDER[1],'stop-cleanup':ORDER[2]};unit=names[action]
 require(len(STOPPED)<3 and unit==ORDER[len(STOPPED)])
 value=snapshot();validate_current(value);require(value==snapshot());peer_check();inventory_check();kernel_scope()
 before=show(unit);require(before==expected_current['units'][unit])
 require(before['ActiveState']=='active'and before['ControlPID']=='0'and before['Job']=='')
 # Durable once-per-actual-generation reservation precedes the only ordinary stop.
 save(unit+'.stop-reserved.private',json.dumps({'before':before,'parent':fixed_parent,'once':True},sort_keys=True).encode())
 issued_us=int(time.clock_gettime(time.CLOCK_MONOTONIC)*1000000)
 result=subprocess.run(['/usr/bin/systemctl','stop',unit],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
 require(result.returncode==0);after=show(unit)
 stable={'Id','LoadState','InvocationID','ExecMainStartTimestampMonotonic','Type','Restart','RemainAfterExit','KillMode','SendSIGKILL'}
 require(all(before[k]==after[k]for k in stable)and after['ActiveState']=='inactive'and after['SubState']=='dead'and after['Result']=='success'and after['MainPID']==after['ControlPID']=='0'and after['Job']=='')
 if unit=='artemis.service':
  require(after['ExecMainCode']=='1'and after['ExecMainStatus']=='143'and int(after['ExecMainExitTimestampMonotonic'])>int(before['ExecMainStartTimestampMonotonic'])and not pathlib.Path('/proc/41805').exists())
 else:require(all(before[k]==after[k]for k in ['ExecMainCode','ExecMainStatus','ExecMainExitTimestampMonotonic']))
 kernel_empty(unit)
 journal=command(['journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+unit,'INVOCATION_ID='+before['InvocationID'],'-o','json','--no-pager'],1048576)
 records=[json.loads(line,object_pairs_hook=unique)for line in journal.splitlines()];old=expected_current['pid1CohortObservations'][unit]['pid1']
 require(len(old)<len(records)<=len(old)+4 and records[:len(old)]==old)
 extra=records[len(old):];require(all(r.get('_PID')=='1'and r.get('_UID')=='0'and r.get('_BOOT_ID')==BOOT.replace('-','')and r.get('UNIT')==unit and r.get('INVOCATION_ID')==before['InvocationID']and int(r['__MONOTONIC_TIMESTAMP'])>=issued_us and r.get('MESSAGE_ID')in {'de5b426a63be47a7b6ac3eaac82e2f6f','9d1aaa27d60140bd96365438aad20286','7ad2d189f7e94e70a38c781354912448','ae8f7b866b0347b9af31fe1c80b127c0'}for r in extra))
 starts=[r for r in extra if r.get('MESSAGE_ID')=='de5b426a63be47a7b6ac3eaac82e2f6f'and r.get('JOB_TYPE')=='stop']
 ends=[r for r in extra if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done']
 require(len(starts)<=1 and len(ends)==1)
 if starts:require(starts[0]['JOB_ID']==ends[0]['JOB_ID']and int(starts[0]['__MONOTONIC_TIMESTAMP'])<=int(ends[0]['__MONOTONIC_TIMESTAMP']))
 # RemainAfterExit oneshot may have only the genuine done receipt: no invented Starting/Stopping.
 vendor=None
 if unit=='artemis.service':
  raw=command(['journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_UNIT='+unit,'_SYSTEMD_INVOCATION_ID='+before['InvocationID'],'-o','json','--no-pager'],4194304)
  vendor=broker_witness(before,after,raw);save('broker.vendor.private.jsonl',raw)
 receipt={'after':after,'pid1':records,'stopJob':ends[0]['JOB_ID'],'vendor':vendor,'root143NotNormalized':True}
 save(unit+'.stopped.private',json.dumps(receipt,sort_keys=True).encode());STOP_RECEIPTS[unit]=receipt;STOPPED.append(unit)
'''
