"""SSC287 candidate dispatcher builder. No recovery entrypoint until independent ABI acceptance.

The emitted payload is separately frozen and reviewed before it can acquire or change runtime.
No normal-parent receipt is manufactured. Root timeout143 remains a failed parent.
"""
import inspect
import pg4112_canonical_epoch_owned_stage as stage
import pg4074_failed_done_parent_contract as parent
import pg4102_failed_done_recovery_protocol as protocol
import pg4122_fixed_terminal_native_contract as native
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4126-fixed-native-owned-recovery-v1'


def payload():
    raw = stage.payload('inspect')
    raw = raw[:raw.index('import dbus\nbus=')].replace(stage.INSPECT, SLOT)
    raw = 'import sys\nif sys.argv[1:] not in (["inspect"],["recover"]):raise ValueError("one explicit dispatch mode required")\nMODE=sys.argv[1]\n' + raw
    raw = once(raw, "save=base/'" + SLOT + "'", "save=base/('" + SLOT + "-'+MODE)")
    raw = once(raw, "b'one readonly diagnostic\\n'", "b'one failed-DONE recovery; no replay\\n'")
    # Existing immutable runtime guard is initially strict; only the explicit terminal map
    # below allows subsequent same-generation unit transitions.
    raw = once(raw, "  if name in expected_inv:require(v['InvocationID']==expected_inv[name] and v['ActiveState']=='active' and v['SubState']=='running')",
               "  if name in expected_inv:require(v['InvocationID']==expected_inv[name])")
    p = inspect.getsource(protocol).replace('from pg4086_failed_done_recovery_contract import ORDER, Plan, require',
                                          'from recovery_plan import ORDER, Plan, require')
    native_source=inspect.getsource(native).replace('from pg4086_failed_done_recovery_contract import require','from recovery_plan import require')
    raw += '\nPARENT_SOURCE=' + repr(inspect.getsource(parent)) + '\nPROTOCOL_SOURCE=' + repr(p) + '\nNATIVE_SOURCE='+repr(native_source)+'\n' + BODY
    compile(raw, '<candidate failed-DONE owned recovery>', 'exec')
    return raw


BODY = r'''
import time,sys
sys.path.insert(0,str(frozen))
import recovery_terminal as terminal_contract
from pg526_term_witness import FIELDS as TERMINAL_FIELDS,unique
parent_contract={};exec(PARENT_SOURCE,parent_contract)
protocol={};exec(PROTOCOL_SOURCE,protocol)
native_contract={};exec(NATIVE_SOURCE,native_contract)
ORDER=protocol['ORDER'];preserved_tree=protocol['preserved_tree']
completed_units={};baseline=None;owned=None;child=None;refs=[];error=None
native_mutable={};native_identities={};holder_ticks=None;holder_args=None
actorraw=Path('/var/lib/pgpt-s1-preservation/pg4080-failed-ordinary-full-capture-v1/observed.private.json').read_bytes()
require(hashlib.sha256(actorraw).hexdigest()=='fd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8')
actor_certificate=json.loads(actorraw);require(actor_certificate['source']==data['source']['commit']and actor_certificate['BOM']==sha and actor_certificate['boot']==boot)
EXPECTED_ACTORS=actor_certificate['second']['actors']
parent_journal=Path('/var/lib/pgpt-s1-preservation/pg4072-failed-parent-pid1-read-v1/pid1.private.jsonl').read_bytes()
require(hashlib.sha256(parent_journal).hexdigest()=='4b930e614069ccaee34382ba14d84efaf1274dafd262749c5a77d61accb10f38')
keys=['MESSAGE_ID','UNIT','INVOCATION_ID','JOB_ID','JOB_TYPE','JOB_RESULT','__MONOTONIC_TIMESTAMP','_PID','_UID','_BOOT_ID']
parent_rows=[json.loads(line,object_pairs_hook=unique)for line in parent_journal.splitlines()]
parent_rows=[{k:v[k]for k in keys if k in v}for v in parent_rows if 128735401165<=int(v['__MONOTONIC_TIMESTAMP'])<=130545470134]
donepath=Path('/var/lib/schubert-nk/maintenance/attempts/d9d58371-bf80-49f6-bad9-3d1e0916fb04.done')
epochpath=Path('/run/schubert-nk/startup/epoch.current');epoch_before=epochpath.read_bytes()
# The text oracle is distinct from the Production typed revoke implementation.
from recovery_plan import invalid_epoch
epoch_expected=invalid_epoch(epoch_before)
def durable_save(name,content):
 require(type(name)is str and '/'not in name and type(content)is bytes and 0<len(content)<=67108864)
 fd=os.open(save/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  offset=0
  while offset<len(content):
   n=os.write(fd,content[offset:]);require(n>0);offset+=n
  os.fsync(fd)
 finally:os.close(fd)
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:os.fsync(fd)
 finally:os.close(fd)
def encode(value):return json.dumps(value,sort_keys=True).encode()
def show_terminal(unit):
 require(unit in ORDER)
 rawshow=command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(TERMINAL_FIELDS))],1048576)
 require(rawshow.endswith(b'\n'))
 v=unique([line.split('=',1)for line in rawshow.decode('ascii').splitlines()])
 require(set(v)==TERMINAL_FIELDS and v['Id']==unit and v['LoadState']=='loaded');return v
def holder():
 require(child is not None and child.poll()is None and owned is not None)
 p=Path('/proc')/str(owned[0]);require((p/'cmdline').read_bytes()==holder_args and int((p/'stat').read_text().rsplit(')',1)[1].split()[19])==holder_ticks)
 status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==['0']*4 and status['Gid'].split()==['0']*4)
 targets={str(fd.readlink())for fd in(p/'fd').iterdir()}
 require(all(str(Path('/run/schubert-nk')/n)in targets for n in ['maintenance.lock','startup-admission.lock']))
 require(not {c for task in(p/'task').iterdir()for c in(task/'children').read_text().split()})
def peer_check(value,held):
 table=[line.split()for family in ['tcp','tcp6']for line in Path('/proc/net',family).read_text().splitlines()[1:]]
 roles={'schubert_app':('schubert-nk-api.service',2),'schubert_web_session':('schubert-nk-web.service',1)}
 expected={k:(0 if u in completed_units else count)for k,(u,count)in roles.items()};counts={k:0 for k in roles}
 actual=value['database']['peers'];require(len(actual)==sum(expected.values())+(1 if held else 0))
 for row in actual:
  require(row['address']=='127.0.0.1'and type(row['port'])is int and row['port']>0)
  if held and row['pid']==owned[1]:
   require(row['user']=='schubert_batch'and row['application']=='PG286-original-profile');pid=owned[0]
  else:
   require(row['user']in roles);unit,_=roles[row['user']];counts[row['user']]+=1;pid=value['actors'][unit]['pid']
  tcp_pair(table,row['port'],inodes(pid),inodes(row['pid']))
 require(counts==expected)
 if held:
  locks=value['database']['locks'];require(len(locks)==1 and locks[0]['pid']==owned[1]and locks[0]['classid']==0 and locks[0]['objid']==71419602 and locks[0]['objsubid']==1 and locks[0]['mode']=='ExclusiveLock'and locks[0]['granted'])
  require(len(value['flocks'])==2 and all(line.split()[4]==str(owned[0])for line in value['flocks']));holder()
 else:require(not value['database']['locks']and not value['flocks'])
def fail_parent(value):
 result=parent_contract['classify'](data['source']['commit'],sha,boot,value['units'][parent_contract['UNIT']],parent_rows,donepath.read_bytes())
 require(result['failedParent143Confirmed']and result['parentNormal']is False)
 terminal_contract.kernel_empty(parent_contract['UNIT']);require(not Path('/proc/696557').exists())
def source_fixed():
 require(manifest.read_bytes()==raw and current.resolve(strict=True)==root and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)
 for filename,expected in old['unitFilesActual'].items():
  p=Path(filename);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==expected)
 require(config()==fixed_config)
def preserved(value,revoked):
 require(value['database']['rows']==baseline['database']['rows']and value['durable']==baseline['durable']and value['runtime']==baseline['runtime'])
 for unit,before in baseline['units'].items():require(value['units'][unit]==completed_units.get(unit,before))
 remaining={u:v for u,v in baseline['actors'].items()if u not in completed_units}
 require(value['actors']==remaining)
 native_contract['preserved'](baseline['native'],value['native'],native_mutable,set(completed_units)&set(native_mutable),native_identities,lambda p:Path(p).read_bytes(),lambda p:os.listxattr(p))
 if revoked:
  require(epochpath.read_bytes()==epoch_expected)
  preserved_tree(baseline['startup'],value['startup'],(str(epochpath),),(str(epochpath.parent),))
 else:require(value['startup']==baseline['startup']and epochpath.read_bytes()==epoch_before)
def checked(held=True,revoked=False):
 first=snapshot();second=snapshot();same_values(first,second)
 require([{k:v for k,v in row.items()if k!='state'}for row in first['database']['peers']]==[{k:v for k,v in row.items()if k!='state'}for row in second['database']['peers']])
 peer_check(first,held);peer_check(second,held);fail_parent(second)
 if baseline is not None:preserved(second,revoked)
 source_fixed();return second
def frame(expected):
 sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ)
 try:require(bool(sel.select(60)));line=child.stdout.readline(201);require(0<len(line)<200 and line.endswith('\n'));require(line.rstrip('\n')==expected)
 finally:sel.close()
def ack():child.stdin.write('CONTINUE\n');child.stdin.flush()
def retain():
 durable_save('unknown.private',b'UNKNOWN; no retry, signal, force unlock, Root replay or acceptance\n')
 print('SSC287_UNKNOWN isolationRetained=true oldRootStillFailed=true',flush=True)
 while True:time.sleep(1)
import dbus
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
try:
 for unit in old['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 fixed_config=config();baseline=snapshot();second=snapshot();same_values(baseline,second);peer_check(second,False);fail_parent(second);source_fixed()
 require(set(baseline['actors'])==set(EXPECTED_ACTORS))
 require(baseline['actors']==EXPECTED_ACTORS)
 for unit in ['schubert-nk-api.service','schubert-nk-web.service']:
  argv=(Path('/proc')/str(baseline['actors'][unit]['pid'])/'cmdline').read_bytes().split(b'\0')
  dest=native_contract['destination'](unit,baseline['units'][unit]['InvocationID'],argv)
  require(dest not in baseline['native']and not os.path.lexists(dest)and str(Path(dest).parent)in baseline['native'])
  native_mutable[unit]=dest;native_identities[unit]=baseline['detailedActors'][unit]['nss']
 require(len(set(native_mutable.values()))==2)
 captures={unit:show_terminal(unit)for unit in ORDER};durable_save('before.private.json',encode(baseline));durable_save('terminal-before.private.json',encode(captures))
 args=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',str(classes)+':'+cp,'dev.codex.schubert.nk.batch.file.RootFailedDoneRecovery',MODE]
 error=(save/'java-stderr.private.log').open('xb');child=subprocess.Popen(args,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=error,text=True,bufsize=1)
 sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ)
 try:require(bool(sel.select(60)));line=child.stdout.readline(201);require(re.fullmatch(r'RECOVERY_READY [1-9][0-9]{0,9}\n',line)is not None)
 finally:sel.close()
 owned=(child.pid,int(line.split()[1]));p=Path('/proc')/str(child.pid);holder_ticks=int((p/'stat').read_text().rsplit(')',1)[1].split()[19]);holder_args=b'\0'.join(a.encode()for a in args)+b'\0'
 checked();durable_save('owned.private.json',encode({'pid':owned[0],'ticks':holder_ticks,'backend':owned[1],'argvSha256':hashlib.sha256(holder_args).hexdigest()}));ack()
 def verify(unit):checked()
 def reserve(unit):durable_save(unit+'.stop-reserved.private',encode({'unit':unit,'before':captures[unit],'holderPid':owned[0],'holderTicks':holder_ticks}))
 def stop(unit):
  require(show_terminal(unit)==captures[unit]);holder()
  r=subprocess.run(['/usr/bin/systemctl','stop',unit],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120);require(r.returncode==0)
 def terminal(unit):
  before=captures[unit];after=show_terminal(unit);require(terminal_contract.terminal(after)and terminal_contract.same_generation(before,after));terminal_contract.kernel_empty(unit)
  if before['MainPID']!='0':require(not(Path('/proc')/before['MainPID']).exists())
  if unit in ['schubert-nk-api.service','schubert-nk-web.service','artemis.service']:
   journal=command(['/usr/bin/journalctl','--boot='+boot.replace('-',''),'_SYSTEMD_INVOCATION_ID='+before['InvocationID'],'-o','json','--no-pager'],4194304)
   if unit=='artemis.service':witness=terminal_contract.broker_witness(before,after,journal)
   else:witness=terminal_contract.witness('API'if unit=='schubert-nk-api.service'else'WEB',before,after,journal,before['MainPID'],str(int(baseline['detailedActors'][unit]['nss']['uid'])))
   durable_save(unit+'.journal.private.jsonl',journal);durable_save(unit+'.witness.private.json',encode(witness))
  else:require(terminal_contract.normal_terminal(before,after))
  require(show_terminal(unit)==after)
  # snapshots carry ControlGroup in addition to terminal fields; capture the exact current projection.
  current_units,_=units();completed_units[unit]=current_units[unit];return True
 def record(unit):durable_save(unit+'.stopped.private.json',encode(completed_units[unit]))
 if MODE=='inspect':
  frame('RECOVERY_INSPECTED');checked();ack()
 else:
  recovery=protocol['Recovery'](verify,reserve,stop,terminal,record)
  for unit in ORDER:
   frame('RECOVERY_STOP '+unit);recovery.one(unit);print('SSC287_STOPPED unit='+unit+' generationVerified=true',flush=True);ack()
  recovery.complete();frame('RECOVERY_TERMINAL');checked();durable_save('all-six-normal.private',b'all six qualified; oldRoot143 remains failed\n');ack()
  frame('RECOVERY_REVOKED');checked(revoked=True);recovery.plan.revoke();durable_save('canonical-revoked.private',encode({'epochSha256':hashlib.sha256(epoch_expected).hexdigest(),'oldParentNormal':False}));ack()
 frame('RECOVERY_CLOSED');post=checked(held=False,revoked=MODE=='recover');durable_save('after.private.json',encode(post));ack()
 remaining=child.communicate(timeout=20)[0];require(child.returncode==0 and remaining=='RECOVERY_NORMAL_RETURN oldParentNormal=false\n');error.close();error=None
 if MODE=='recover':recovery.plan.finish()
 require(not(Path('/proc')/str(owned[0])).exists());checked(held=False,revoked=MODE=='recover')
except BaseException:
 # If a child/scope ever existed, preserve it rather than unwinding unknown ownership.
 if child is not None:retain()
 raise
finally:
 if child is None or child.returncode==0:
  if error is not None:error.close()
  for unit in reversed(refs):manager.UnrefUnit(unit)
  bus.close()
result={'actualExit':0,'source':data['source']['commit'],'BOM':sha,'boot':boot,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':MODE,'oldRoot143StillFailed':True,'oldParentNormal':False,'recoverySixNormal':MODE=='recover','canonicalEpochRevoked':MODE=='recover','all33StartupEntriesPreserved':True,'newScopeNormalClose':True,'independentPostRequired':MODE=='recover','formalAccepted':False,'productionPtAdded':0}
durable_save('manifest.safe.json',encode(result));print(json.dumps(result))
'''
