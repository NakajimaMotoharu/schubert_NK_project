"""SSC271 fresh normal verify-only of already canonical runtime; no write/reload."""
from pg1559_pending_runtime_sources import java as prior_java,refs as prior_refs,CLASS as OLD_CLASS,TOOLS as OLD_TOOLS,SAVE as OLD_SAVE,RUNTIME_FUNCTIONS
from pg1553_pending_publication_java import once

CLASS='Pg1567ExistingRuntime'
TOOLS='pg1567-existing-runtime-tools-v1'
SAVE='pg1569-existing-runtime-verify-v1'

def java():
    return prior_java().replace(OLD_CLASS,CLASS).replace(OLD_TOOLS,TOOLS).replace(OLD_SAVE,SAVE).replace('pg1559_pending_runtime_refs.py','pg1567_existing_runtime_refs.py').replace('PG1562_','PG1569_').replace('PG271-runtime-once','PG272-runtime-verify').replace('"prepare".equals(args[0])','"verify-existing".equals(args[0])').replace('onceRuntimePrepared','existingRuntimeVerified')

def refs():
    s=prior_refs().replace(OLD_CLASS,CLASS).replace(OLD_TOOLS,TOOLS).replace(OLD_SAVE,SAVE).replace('PG271-runtime-once','PG272-runtime-verify').replace("b'prepare'","b'verify-existing'")
    s=once(s,RUNTIME_FUNCTIONS,VERIFY_FUNCTIONS)
    s=once(s,"  if action=='prepared':\n   require(not runtime_changed);writer.owned_prepare(runtime_parent,dropin);runtime_changed=True\n   command(['/usr/bin/systemctl','daemon-reload'],4096)\n",'')
    s=s.replace('pg1558-pending-publication-independent-closing-v1/observed.private.json','pg1566-retained-runtime-pair-closing-v1/after.private.json').replace('c08641a127bffc84256619574a3333a7ce64552a62a843f916cdd3fcded50046','978f6867d38a186ab3a18a30bbc93827f2c5318203d671ccc77119ee36b13ef2')
    s=once(s,"'oneTimeRuntime': tree(pathlib.Path('/run/systemd/system'))", "'oneTimeRuntime': runtime_rows()")
    s=s.replace("'onceRuntimePrepared':True", "'existingRuntimeVerified':True")
    compile(s,'<fresh normal canonical runtime verification>','exec');return s

VERIFY_FUNCTIONS=r'''
import pg1559_pending_runtime_writer as writer
from pg1090_cold_finite_capture import direct_tree
MORNING='schubert-nk-morning-controller.service'
RUNTIME=pathlib.Path('/run/systemd/system')
dropin=None
def runtime_rows():
 root=str(RUNTIME);directory=str(RUNTIME/writer.UNIT);file=str(RUNTIME/writer.UNIT/writer.NAME)
 value=direct_tree(root);require(set(value)=={root,directory})
 child=direct_tree(directory);require(set(child)=={directory,file}and child[directory]==value[directory]);value.update(child)
 return value
def initialize_runtime():
 global dropin
 dropin=writer.fixed_dropin(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544/systemd/schubert-nk-morning-controller.service').read_bytes(),pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
 require(writer.NAME=='zz-pg1160-once-resume.conf'and writer.RUN_ID=='15700a87-9117-4f63-a0ff-768dd604d0f1')
 require(command(['findmnt','-n','-o','FSTYPE','--target',str(RUNTIME)],4096).strip()==b'tmpfs')
def configuration_permitted(unit,value):
 require(value==profile_expected['configuration'][unit])
 if unit==MORNING:
  record=exec_record(value['ExecStart']);require(record is not None)
  line=[l[10:]for l in dropin.decode('ascii').splitlines()if l.startswith('ExecStart=')and len(l)>10]
  require(len(line)==1 and record[0]=='/usr/bin/java'and record[1]==line[0]and record[2]=='no')
  require(value['DropInPaths']=='/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf /run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf')
def protected_runtime(value):
 require(type(value)is dict and type(value.get('oneTimeRuntime'))is dict)
 actual=dict(value);runtime=actual.pop('oneTimeRuntime');expected=dict(profile_expected);fixed=expected.pop('oneTimeRuntime')
 require(set(runtime)==set(fixed))
 normalized={}
 for path,row in runtime.items():
  require(type(row)is dict and set(row)=={'metadata','sha256','target','acl'}and type(row['metadata'])is list and len(row['metadata'])==9 and all(type(n)is int and n>=0 for n in row['metadata'])and row['target']is None and row['acl']==[])
  normalized[path]={'metadata':row['metadata'],'sha256':row['sha256']}
 require(normalized==fixed)
 root=str(RUNTIME);directory=str(RUNTIME/writer.UNIT);target=directory+'/'+writer.NAME
 require(runtime[root]['metadata'][2:6]==[0,0,stat.S_IFDIR|0o755,3]and runtime[directory]['metadata'][2:6]==[0,0,stat.S_IFDIR|0o755,2])
 require(runtime[target]['metadata'][2:7]==[0,0,stat.S_IFREG|0o644,1,len(dropin)]and runtime[target]['sha256']==hashlib.sha256(dropin).hexdigest())
 require(actual==expected)
'''
