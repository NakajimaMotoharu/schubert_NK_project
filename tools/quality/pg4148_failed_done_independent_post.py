"""SSC287 candidate fresh independent post. Builder only; no premature execution entrypoint."""
import ast
import inspect
import json
import pg4064_original_profile_typed_oid as previous
import pg4058_original_read_profile as transport
import pg4080_failed_ordinary_full_capture as authority
import pg4074_failed_done_parent_contract as parent
import pg4102_failed_done_recovery_protocol as tree
import pg4122_fixed_terminal_native_contract as native
import pg4132_signed_phase_invariant as signed
import pg4138_independent_revoked_epoch as epoch
import pg4112_canonical_epoch_owned_stage as role
from pg4060_original_profile_dual_stack import once

SLOT='pg4148-failed-done-independent-post-v1'
RECOVERY='/var/lib/pgpt-s1-preservation/pg4146-complete-signed-owned-recovery-v1-recover'


def payload():
    raw=previous.payload('run').replace(previous.SLOT,SLOT)
    raw=once(raw,"  if name in expected_inv:require(v['InvocationID']==expected_inv[name] and v['ActiveState']=='active' and v['SubState']=='running')",
             "  if name in expected_inv:require(v['InvocationID']==expected_inv[name])")
    raw=once(raw,"roles={'schubert_app':('schubert-nk-api.service',2),'schubert_web_session':('schubert-nk-web.service',1)};counts={k:0 for k in roles}",
             "roles={};counts={}")
    raw=once(raw,"require(len(actual)==(4 if owned else 3))","require(len(actual)==(1 if owned else 0))")
    extra=[]
    for n in ast.parse(authority.BODY).body:
        if isinstance(n,ast.FunctionDef)and n.name=='nss':extra.append(ast.get_source_segment(authority.BODY,n))
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='accounts'for t in n.targets):extra.append(ast.get_source_segment(authority.BODY,n))
    fixed=json.loads((transport.W/(role.TOOLS+'-compile')/'manifest.safe.json').read_bytes())
    if fixed['actualExit']!=0:raise ValueError('qualified fixed witness closure first')
    embedded={'NATIVE_SOURCE':inspect.getsource(native).replace('from pg4086_failed_done_recovery_contract import require','from recovery_plan import require'),
              'EPOCH_SOURCE':inspect.getsource(epoch).replace('from pg4086_failed_done_recovery_contract import invalid_epoch,require','from recovery_plan import invalid_epoch,require'),
              'TREE_SOURCE':inspect.getsource(tree).replace('from pg4086_failed_done_recovery_contract import ORDER, Plan, require','from recovery_plan import ORDER, Plan, require'),'SIGNED_SOURCE':signed.source(),'PARENT_SOURCE':inspect.getsource(parent)}
    prefix='\n'.join(k+'='+repr(v)for k,v in embedded.items())+'\nHELPERS='+repr(fixed['result']['inputFileHashes'])+'\nTOOLS='+repr(role.TOOLS)+'\nRECOVERY='+repr(RECOVERY)+'\n'+'\n'.join(extra)+'\n'+PRECHECK
    raw=once(raw,'import dbus\nbus=',prefix+'\nimport dbus\nbus=')
    raw=once(raw,"'newMARDDBTenRefNormalClose':True","'newMARDDBTenRefNormalClose':True,'independentFailedDoneRecoveryPost':True,'oldParentNormal':False,'nativeQualificationPending':True")
    compile(raw,'<fresh independent failed-DONE post>','exec');return raw


PRECHECK=r'''
import sys
fields+=',Type,Restart,RemainAfterExit,KillMode,SendSIGKILL'
frozen_witness=Path('/var/lib/pgpt-s1-preservation')/TOOLS
for name,digest in HELPERS.items():
 p=frozen_witness/name;m=metadata(p);s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest and metadata(p)==m)
sys.path.insert(0,str(frozen_witness))
import recovery_terminal as terminal_contract
from pg526_term_witness import FIELDS as TERMINAL_FIELDS,unique
native_contract={};exec(NATIVE_SOURCE,native_contract)
epoch_contract={};exec(EPOCH_SOURCE,epoch_contract)
tree_contract={};exec(TREE_SOURCE,tree_contract)
signed_contract={};exec(SIGNED_SOURCE,signed_contract)
parent_contract={};exec(PARENT_SOURCE,parent_contract)
fixed_materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]
reference=Path('/var/lib/pgpt-s1-preservation/pg4080-failed-ordinary-full-capture-v1/observed.private.json').read_bytes()
require(hashlib.sha256(reference).hexdigest()=='fd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8')
reference=json.loads(reference);require(reference['source']==data['source']['commit']and reference['BOM']==sha and reference['boot']==boot);reference=reference['second']
receipt_path=Path(RECOVERY)/'manifest.safe.json';rm=metadata(receipt_path);s=receipt_path.lstat()
require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(receipt_path)and 0<s.st_size<=65536)
receipt_raw=receipt_path.read_bytes();receipt=json.loads(receipt_raw,object_pairs_hook=unique);require(metadata(receipt_path)==rm)
require(receipt['source']==data['source']['commit']and receipt['BOM']==sha and receipt['boot']==boot and receipt['mode']=='recover'and receipt['actualExit']==0 and receipt['oldParentNormal']is False and all(receipt[k]is True for k in ['oldRoot143StillFailed','recoverySixNormal','canonicalEpochRevoked','all33StartupEntriesPreserved','newScopeNormalClose','independentPostRequired']))
# DB preservation is an independent SQL before/after condition, not equality to an hours-old
# observation of a still-running ordinary application. Never generate expected rows via Production.
before_path=Path(RECOVERY)/'before.private.json';bm=metadata(before_path);bs=before_path.lstat()
require(stat.S_ISREG(bs.st_mode)and(bs.st_uid,bs.st_gid,stat.S_IMODE(bs.st_mode),bs.st_nlink)==(0,0,0o600,1)and not os.listxattr(before_path)and 0<bs.st_size<=67108864)
before_raw=before_path.read_bytes();before=json.loads(before_raw,object_pairs_hook=unique);require(metadata(before_path)==bm)
require(before['actors']==reference['actors']and len(before['database']['rows'])==24 and set(before['database']['rows'])==set(reference['database']['rows']))
require(all(before['units'][unit]['InvocationID']==reference['units'][unit]['InvocationID']for unit in reference['units']))
parent_raw=Path('/var/lib/pgpt-s1-preservation/pg4072-failed-parent-pid1-read-v1/pid1.private.jsonl').read_bytes()
require(hashlib.sha256(parent_raw).hexdigest()=='4b930e614069ccaee34382ba14d84efaf1274dafd262749c5a77d61accb10f38')
keys=['MESSAGE_ID','UNIT','INVOCATION_ID','JOB_ID','JOB_TYPE','JOB_RESULT','__MONOTONIC_TIMESTAMP','_PID','_UID','_BOOT_ID']
rows=[json.loads(line,object_pairs_hook=unique)for line in parent_raw.splitlines()]
rows=[{k:v[k]for k in keys if k in v}for v in rows if 128735401165<=int(v['__MONOTONIC_TIMESTAMP'])<=130545470134]
exports={};identities={}
for unit,(label,directory)in native_contract['ROLES'].items():
 inv=reference['units'][unit]['InvocationID']
 argument=('-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid='+label+'-'+inv+'-ordinary').encode('ascii')
 exports[unit]=native_contract['destination'](unit,inv,[argument]);identities[unit]=nss(unit)
 require(identities[unit]==reference['detailedActors'][unit]['nss'])
original_snapshot=snapshot
def snapshot():
 require(signed_contract['verify'](str(root),data['artifacts'],raw,fixed_materials)is True)
 value=original_snapshot();require(not value['actors'])
 require(value['database']['rows']==before['database']['rows']and value['durable']==before['durable']and value['runtime']==before['runtime'])
 native_contract['preserved'](before['native'],value['native'],exports,set(exports),identities,lambda p:Path(p).read_bytes(),lambda p:os.listxattr(p))
 for unit in tree_contract['ORDER']:
  b={k:reference['units'][unit][k]for k in TERMINAL_FIELDS};a={k:value['units'][unit][k]for k in TERMINAL_FIELDS}
  terminal_contract.kernel_empty(unit)
  if b['MainPID']!='0':require(not(Path('/proc')/b['MainPID']).exists())
  if unit in ['schubert-nk-api.service','schubert-nk-web.service','artemis.service']:
   journal=command(['/usr/bin/journalctl','--boot='+boot.replace('-',''),'_SYSTEMD_INVOCATION_ID='+b['InvocationID'],'-o','json','--no-pager'],4194304)
   if unit=='artemis.service':terminal_contract.broker_witness(b,a,journal)
   else:terminal_contract.witness('API'if unit=='schubert-nk-api.service'else'WEB',b,a,journal,b['MainPID'],str(identities[unit]['uid']))
  else:require(terminal_contract.normal_terminal(b,a))
 for unit in set(reference['units'])-set(tree_contract['ORDER']):
  require(all(value['units'][unit][key]==item for key,item in reference['units'][unit].items()if key in value['units'][unit]))
 parent_contract['classify'](data['source']['commit'],sha,boot,value['units'][parent_contract['UNIT']],rows,Path('/var/lib/schubert-nk/maintenance/attempts/d9d58371-bf80-49f6-bad9-3d1e0916fb04.done').read_bytes())
 terminal_contract.kernel_empty(parent_contract['UNIT']);require(not Path('/proc/696557').exists())
 epoch=Path('/run/schubert-nk/startup/epoch.current');current_epoch=epoch.read_bytes()
 # Validate canonical UUID before it can become a fixed private permit filename.
 validated=epoch_contract['former_issued'](current_epoch,'0'*64);epoch_id=validated.decode('ascii').split('\n')[3].split('=',1)[1]
 permit=epoch.parent/(epoch_id+'.permit');require(str(permit)in before['startup'])
 permit_sha=hashlib.sha256(permit.read_bytes()).hexdigest();require(permit_sha==before['startup'][str(permit)]['sha256'])
 issued=epoch_contract['former_issued'](current_epoch,permit_sha);require(hashlib.sha256(issued).hexdigest()==before['startup'][str(epoch)]['sha256'])
 require(not os.listxattr(epoch));tree_contract['preserved_tree'](before['startup'],value['startup'],(str(epoch),),(str(epoch.parent),))
 require(receipt_path.read_bytes()==receipt_raw and metadata(receipt_path)==rm and before_path.read_bytes()==before_raw and metadata(before_path)==bm)
 return value
'''
