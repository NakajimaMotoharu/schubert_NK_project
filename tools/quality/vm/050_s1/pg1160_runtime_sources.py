"""SSC259 current same-active finite runtime; no Root start or permit issuance."""
import ast
import inspect
from pathlib import Path
from pg1148_native_five_sources import preparation as previous_java, refs as previous_refs
from pg1134_failed_recovery_sources import replace
from pg870_ordinary_before import parser_source
import pg1160_runtime_writer as writer

HERE=Path(__file__).resolve().parent
BASE='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/native-five-post-v1/after.private.json'
HASH='03d3aab26b1da00c6c68cad0a54fc1dbd5074c82fa961036a732fdb24f78b612'


def bind(s):
    return s.replace('Pg1148NativeRolePreparation','Pg1160RuntimeResume').replace('PG1148','PG1160').replace('pg1148_native_role_refs.py','pg1160_runtime_refs.py').replace('pg1148-native-five-recovery-v1','pg1160-runtime-resume-v1').replace('pg1148-native-five-tools-v1','pg1160-runtime-tools-v1')


def java():
    s=bind(previous_java());start=s.index('      refs.check("terminal");');end=s.index('      refs.check("prepared");',start)
    s=s[:start]+'      refs.check("terminal");phase="FIXED_RUNTIME_PREPARATION";refs.check("prepare");\n'+s[end:]
    s=s.replace('f.getClassName().startsWith("Pg513")', 'f.getClassName().equals("Pg1160RuntimeResume") || f.getClassName().startsWith("Pg513")')
    return s.replace('nativeRoles5Prepared','onceResumePrepared').replace('nativePartialPreserved','runtimePartialPreserved')


def refs():
    s=bind(previous_refs()).replace('terminal-management-post-v1/after.private.json','native-five-post-v1/after.private.json').replace('cfd139237f179e7531b94d28c1570c07af9612b476857f3eb479d9a732a7c0b9',HASH)
    s=s.replace('import dbus\n','import dbus\nimport pg1160_runtime_writer as runtime\n')
    # Frozen native tree must remain exactly equal: directory preparation is done.
    s=replace(s,'require(coverage_delta(actual,previous,ids))','require(actual==previous)')
    s=replace(s,"require({u:show(u,configuration_fields()) for u in UNITS}==baseline['configuration'])","configuration=runtime_configuration();require_runtime_configuration(configuration)\n require_runtime_tree()")
    s=replace(s,"return {'rows':rows,'trees':roots}","return {'rows':rows,'trees':roots,'units':{u:show(u,FIELDS)for u in UNITS},'configuration':configuration,'runtime':runtime_tree()}")
    marker='def execute():\n';s=replace(s,marker,EXTRA+marker)
    s=replace(s,'global backend,baseline,owner,revoked_phase,invalid_hash,invalid_length','global backend,baseline,owner,revoked_phase,invalid_hash,invalid_length,runtime_parent,dropin,changed')
    s=replace(s," backend=int(sys.argv[1]);owner=holder();identity()", " runtime_parent=metadata(pathlib.Path('/run/systemd/system'));require(runtime_parent[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr('/run/systemd/system')and not list(pathlib.Path('/run/systemd/system').iterdir()))\n dropin=runtime.fixed_dropin(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1068/systemd/schubert-nk-morning-controller.service').read_bytes(),pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes());changed=False\n backend=int(sys.argv[1]);owner=holder();identity()")
    s=replace(s,"['before','terminal','roles','prepared','release']","['before','terminal','prepare','prepared','release']")
    s=replace(s,"   if action=='prepared':\n", "   if action=='prepare':\n    require(not changed);runtime.owned_prepare(runtime_parent,dropin);changed=True\n    command(['/usr/bin/systemctl','daemon-reload']);require_runtime_configuration(runtime_configuration());require_runtime_tree()\n   if action=='prepared':\n")
    start=s.index("    require(set(pathlib.Path(COVERAGE).iterdir())");end=s.index("    namespace_config();save('prepared.private.json'",start)
    s=s[:start]+"    require(changed);require_runtime_tree();retired=True\n"+s[end:]
    s=replace(s,"save('before.private.json',json.dumps(v,sort_keys=True).encode())", "save('before.private.json',json.dumps(v,sort_keys=True).encode());save('new-runtime.private',dropin)")
    s=''+parser_source()+s
    ast.parse(s);return s


EXTRA=r'''
RUNTIME=pathlib.Path('/run/systemd/system')
MORNING='schubert-nk-morning-controller.service'
def runtime_configuration():return {u:show(u,configuration_fields())for u in UNITS}
def require_runtime_configuration(actual):
 require(set(actual)==set(baseline['configuration']))
 for unit,old in baseline['configuration'].items():
  new=actual[unit];require(set(new)==set(old))
  if changed and unit==MORNING:
   require(all(new[k]==old[k]for k in old.keys()-{'ExecStart','DropInPaths'}))
   left=exec_record(old['ExecStart']);right=exec_record(new['ExecStart']);require(left is not None and right is not None)
   require(right[:3]==(left[0],left[1]+' --resume '+runtime.RUN_ID,left[2]))
   require(new['DropInPaths']==old['DropInPaths']+' '+str(RUNTIME/runtime.UNIT/runtime.NAME))
  else:require(new==old)
def runtime_tree():return tree(RUNTIME)
def require_runtime_tree():
 value=runtime_tree();m=value[str(RUNTIME)]['metadata']
 if not changed:require(m==runtime_parent and set(value)=={str(RUNTIME)})
 else:
  directory=RUNTIME/runtime.UNIT;target=directory/runtime.NAME
  require(set(value)=={str(RUNTIME),str(directory),str(target)}and m[:5]==runtime_parent[:5]and m[5]==runtime_parent[5]+1 and m[6]>=runtime_parent[6]and m[7]>=runtime_parent[7]and m[8]>=runtime_parent[8])
  require(value[str(directory)]['metadata'][2:6]==[0,0,stat.S_IFDIR|0o755,2]and value[str(target)]['metadata'][2:7]==[0,0,stat.S_IFREG|0o644,1,len(dropin)])
  require(target.read_bytes()==dropin and value[str(target)]['sha256']==hashlib.sha256(dropin).hexdigest())
 require(command(['/usr/bin/findmnt','--target',str(RUNTIME),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
'''


def files():return {'Pg1160RuntimeResume.java':java(),'pg1160_runtime_refs.py':refs(),'pg1160_runtime_writer.py':inspect.getsource(writer)}
