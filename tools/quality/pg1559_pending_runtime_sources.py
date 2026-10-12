"""SSC270 current pending source -> fixed cold one-time runtime, start/epoch0."""
import ast
import inspect
import sys
from pathlib import Path
from pg1553_pending_publication_java import java as previous_java,PUBLICATION,VERIFY_AND_PUBLISH,once
from pg1546_pending_candidate_ro_sources import refs as previous_refs,CANDIDATE_HELD,POST_RO
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
import pg1160_runtime_writer as old_writer

CLASS='Pg1559PendingRuntime'
TOOLS='pg1559-pending-runtime-tools-v2'
SAVE='pg1562-pending-runtime-v1'
SOURCE='4d6bcbddb417b76d27e52d5d9640752c300edccf'
BOM='e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'
RUN='15700a87-9117-4f63-a0ff-768dd604d0f1'

def writer():
    return inspect.getsource(old_writer).replace("NAME='pg1160-once-resume.conf'","NAME='zz-pg1160-once-resume.conf'").replace(old_writer.RUN_ID,RUN)

def java():
    s=previous_java().replace('Pg1553PendingPublication',CLASS).replace('pg1553-pending-publication-tools-v1',TOOLS).replace('pg1556-pending-publication-v1',SAVE).replace('pg1553_pending_publication_refs.py','pg1559_pending_runtime_refs.py').replace('PG1556_','PG1562_').replace('PG270-pending-code','PG271-runtime-once')
    s=once(s,PUBLICATION,'')
    s=once(s,VERIFY_AND_PUBLISH,'              refs.check("prepared");original(session);\n')
    s=once(s,'"activate".equals(args[0])','"prepare".equals(args[0])')
    s=once(s,'Set.of("prepare","approval","exchange","run")','Set.of("prepare","prepared","run")')
    s=s.replace('PG1292','PG1544').replace('pg1292','pg1544').replace('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE).replace('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM)
    s=once(s,'database.setReadOnly(true);database.setAutoCommit(false);','database.setReadOnly(false);database.setTransactionIsolation(java.sql.Connection.TRANSACTION_READ_COMMITTED);database.setAutoCommit(false);')
    s=once(s,'"PG271-runtime-once","schubert_nk",true,true','"PG271-runtime-once","schubert_nk",false,true')
    return s.replace('pendingCodeOnly','onceRuntimePrepared')

def refs():
    s=previous_refs();s=once(s,CANDIDATE_HELD,'');s=once(s,POST_RO,'')
    for a,b in [('Pg1546PendingCandidateHostRo',CLASS),('pg1546-pending-candidate-ro-tools-v1',TOOLS),('pg1549-pending-candidate-host-ro-v1',SAVE),('PG269-candidate-ro','PG271-runtime-once'),("b'prepare-ro'","b'prepare'"),('PG1292','PG1544'),('pg1292','pg1544'),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE),('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM),('97fd4c41a795c5f2465cf2f5074831723db0c3942fa8d62d16a5aad54cb318f7','fed7f4c24a2356f095aed4310c5a826f9896452cc731971fbd3589f94ae6d232')]:s=s.replace(a,b)
    s=s.replace('pg1511-publication-gc-closing-v1/observed.private.json','pg1558-pending-publication-independent-closing-v1/observed.private.json').replace('7cc53215980eadb5d6d788d1df0b997111b3f6beabc6eef4803f4506afb36ea5','c08641a127bffc84256619574a3333a7ce64552a62a843f916cdd3fcded50046')
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    old=ast.unparse(node);new=once(old,"require(CONFIG_CONTRACT['same'](old['configuration'][n], value, exec_record))","configuration_permitted(n, value)")
    new=once(new,"'brokerActor': actor", "'brokerActor': actor, 'oneTimeRuntime': tree(pathlib.Path('/run/systemd/system'))")
    s=once(s,old,new)
    s=once(s,'  value=snapshot();require(value==profile_expected and value==snapshot());peer_check();inventory_check();return value','  value=snapshot();protected_runtime(value);require(value==snapshot());peer_check();inventory_check();return value')
    marker='try:\n phase=';i=s.index(marker);s=s[:i]+RUNTIME_FUNCTIONS+'\n'+s[i:]
    s=once(s,"first=verify_current();framing('REF_READY')","initialize_runtime();first=verify_current();framing('REF_READY')")
    s=once(s,"  if action=='run':PEER_CLOSED=True", "  if action=='prepared':\n   require(not runtime_changed);writer.owned_prepare(runtime_parent,dropin);runtime_changed=True\n   command(['/usr/bin/systemctl','daemon-reload'],4096)\n  if action=='run':PEER_CLOSED=True")
    s=s.replace("'candidateOnlyHostRo':True,'currentApprovalEpochDbUnitsPreserved':True", "'onceRuntimePrepared':True,'allOriginalDbEpochPermitPreserved':True")
    compile(s,'<current finite cold runtime observer>','exec');return s

RUNTIME_FUNCTIONS=r'''
import pg1559_pending_runtime_writer as writer
MORNING='schubert-nk-morning-controller.service'
RUNTIME=pathlib.Path('/run/systemd/system')
runtime_changed=False;runtime_parent=None;runtime_before=None;dropin=None
def initialize_runtime():
 global runtime_parent,runtime_before,dropin
 runtime_parent=metadata(RUNTIME);runtime_before=tree(RUNTIME)
 require(runtime_parent[2:6]==[0,0,stat.S_IFDIR|0o755,2]and set(runtime_before)=={str(RUNTIME)}and not os.listxattr(RUNTIME))
 require(command(['findmnt','-n','-o','FSTYPE','--target',str(RUNTIME)],4096).strip()==b'tmpfs')
 dropin=writer.fixed_dropin(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544/systemd/schubert-nk-morning-controller.service').read_bytes(),pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
 require(writer.NAME=='zz-pg1160-once-resume.conf'and writer.RUN_ID=='15700a87-9117-4f63-a0ff-768dd604d0f1')
def configuration_permitted(unit,value):
 fixed=profile_expected['configuration'][unit]
 require(set(value)==set(fixed))
 if not runtime_changed or unit!=MORNING:require(value==fixed);return
 require(all(value[k]==fixed[k]for k in fixed.keys()-{'ExecStart','DropInPaths'}))
 left=exec_record(fixed['ExecStart']);right=exec_record(value['ExecStart']);require(left is not None and right is not None)
 require(right[:3]==(left[0],left[1]+' --resume '+writer.RUN_ID,left[2]))
 require(value['DropInPaths']==fixed['DropInPaths']+' '+str(RUNTIME/writer.UNIT/writer.NAME))
def protected_runtime(value):
 actual=dict(value);runtime=actual.pop('oneTimeRuntime');m=runtime[str(RUNTIME)]['metadata']
 if not runtime_changed:require(runtime==runtime_before)
 else:
  directory=RUNTIME/writer.UNIT;target=directory/writer.NAME
  require(set(runtime)=={str(RUNTIME),str(directory),str(target)}and m[:5]==runtime_parent[:5]and m[5]==runtime_parent[5]+1 and m[6]>=runtime_parent[6]and m[7]>=runtime_parent[7]and m[8]>=runtime_parent[8])
  require(runtime[str(directory)]['metadata'][2:6]==[0,0,stat.S_IFDIR|0o755,2]and runtime[str(directory)]['acl']==[])
  require(runtime[str(target)]['metadata'][2:7]==[0,0,stat.S_IFREG|0o644,1,len(dropin)]and runtime[str(target)]['acl']==[]and target.read_bytes()==dropin and runtime[str(target)]['sha256']==hashlib.sha256(dropin).hexdigest())
 for unit,config in actual['configuration'].items():configuration_permitted(unit,config)
 actual['configuration']=profile_expected['configuration'];require(actual==profile_expected)
'''
