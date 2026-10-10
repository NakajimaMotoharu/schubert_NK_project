"""SSC260 correct zz same-active runtime, frozen independent1171 before."""
import ast
from pg1160_runtime_sources import java as previous_java,refs as previous_refs
from pg1134_failed_recovery_sources import replace
from pg1172_existing_runtime_writer import source as writer_source

BASE='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/wrong-runtime-post-v1/after.private.json'
HASH='a936fd3e8f851255acc66156a99db967b52195033dea4b75cf2515e3bce7b36c'


def bind(s):return s.replace('Pg1160RuntimeResume','Pg1172RuntimeResume').replace('PG1160','PG1172').replace('pg1160_runtime_refs.py','pg1172_runtime_refs.py').replace('pg1160_runtime_writer','pg1172_runtime_writer').replace('pg1160-runtime-resume-v1','pg1172-runtime-resume-v1').replace('pg1160-runtime-tools-v1','pg1172-runtime-tools-v1')


def refs():
    s=bind(previous_refs()).replace('native-five-post-v1/after.private.json','wrong-runtime-post-v1/after.private.json').replace('03d3aab26b1da00c6c68cad0a54fc1dbd5074c82fa961036a732fdb24f78b612',HASH)
    s=replace(s,"RUNTIME=pathlib.Path('/run/systemd/system')","RUNTIME=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')")
    s=replace(s,"str(RUNTIME/runtime.UNIT/runtime.NAME)","str(RUNTIME/runtime.NAME)")
    start=s.index(" runtime_parent=metadata(pathlib.Path('/run/systemd/system'));");end=s.index('\n dropin=',start)
    s=s[:start]+" runtime_parent=metadata(RUNTIME);require(runtime_parent[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(RUNTIME)and not list(RUNTIME.iterdir()))\n require(tree(pathlib.Path('/run/systemd/system'))==baseline['runtime'])"+s[end:]
    start=s.index('def require_runtime_tree():');end=s.index('def execute():',start)
    s=s[:start]+TREE+s[end:]
    s='import re\n'+s
    ast.parse(s);return s


TREE=r'''
def require_runtime_tree():
 value=runtime_tree();m=value[str(RUNTIME)]['metadata']
 if not changed:require(m==runtime_parent and set(value)=={str(RUNTIME)})
 else:
  target=RUNTIME/runtime.NAME
  require(set(value)=={str(RUNTIME),str(target)}and m[:6]==runtime_parent[:6]and m[6]>=runtime_parent[6]and m[7]>=runtime_parent[7]and m[8]>=runtime_parent[8])
  require(value[str(target)]['metadata'][2:7]==[0,0,stat.S_IFREG|0o644,1,len(dropin)]and target.read_bytes()==dropin and value[str(target)]['sha256']==hashlib.sha256(dropin).hexdigest())
 parent=pathlib.Path('/run/systemd/system');require({p.name for p in parent.iterdir()}=={runtime.UNIT})
 require(tree(parent)[str(parent)]==baseline['runtime'][str(parent)])
 require(command(['/usr/bin/findmnt','--target',str(RUNTIME),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')
'''


def files():return {'Pg1172RuntimeResume.java':bind(previous_java()),'pg1172_runtime_refs.py':refs(),'pg1172_runtime_writer.py':writer_source()}
