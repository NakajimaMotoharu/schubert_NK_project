"""SSC260 fixed typed wrong-runtime retirement, continuous new ownership."""
import ast
import inspect
from pg1160_runtime_sources import java as previous_java,refs as previous_refs,EXTRA
from pg1134_failed_recovery_sources import replace

BASE='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/runtime-failed-owner-handoff-v1/after.private.json'
HASH='54e3746b8c88dfd3ceca863bc772be601362a645b22c3e2020368a464737b396'


def bind(s):return s.replace('Pg1160RuntimeResume','Pg1166WrongRuntimeRetirement').replace('PG1160','PG1166').replace('pg1160_runtime_refs.py','pg1166_wrong_runtime_refs.py').replace('pg1160-runtime-tools-v1','pg1166-runtime-tools-v1').replace('pg1160-runtime-resume-v1','pg1166-runtime-retirement-v1')


def java():
    s=bind(previous_java());s=replace(s,'refs.check("terminal");phase="FIXED_RUNTIME_PREPARATION";refs.check("prepare");',JAVA)
    return s.replace('onceResumePrepared','wrongRuntimeRetired')


JAVA=r'''refs.check("terminal");phase="FIXED_WRONG_RUNTIME_RETIREMENT";
      byte[] expected=Files.readAllBytes(SAVE.resolve("runtime-before.private"));
      require(expected.length==647);
      try(var runtime=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/systemd/system/schubert-nk-morning-controller.service.d"))){
        dev.codex.schubert.nk.batch.file.Pg1166WrongRuntimeEntry.retire(runtime,expected,()->refs.check("before"));
      }
      require(!Files.exists(Path.of("/run/systemd/system/schubert-nk-morning-controller.service.d/pg1160-once-resume.conf"),LinkOption.NOFOLLOW_LINKS));
      Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","daemon-reload");refs.check("removed");'''


def refs():
    s=bind(previous_refs()).replace('native-five-post-v1/after.private.json','runtime-failed-owner-handoff-v1/after.private.json').replace('03d3aab26b1da00c6c68cad0a54fc1dbd5074c82fa961036a732fdb24f78b612',HASH)
    s=s.replace('import pg1160_runtime_writer as runtime\n','')
    start=s.index('RUNTIME=pathlib.Path(');end=s.index('def execute():',start);s=s[:start]+RETIRE_EXTRA+s[end:]
    start=s.index(" runtime_parent=metadata(pathlib.Path('/run/systemd/system'));");end=s.index(' backend=int(sys.argv[1]);',start)
    s=s[:start]+" runtime_parent=metadata(RUNTIME);require_runtime_tree_initial();dropin=(RUNTIME/'pg1160-once-resume.conf').read_bytes();changed=False\n"+s[end:]
    s=replace(s,"['before','terminal','prepare','prepared','release']","['before','terminal','removed','prepared','release']")
    start=s.index("   if action=='prepare':");end=s.index("   if action=='prepared':",start)
    s=s[:start]+"   if action=='removed':\n    require(not changed);changed=True\n    require_runtime_tree();require_runtime_configuration(runtime_configuration())\n"+s[end:]
    # Removal is performed by typed Java; observation switches before reading removed state.
    s=replace(s,'   all_terminal();v=values();require(v==values())',"   if action=='removed':changed=True\n   all_terminal();v=values();require(v==values())")
    s=s.replace("    require(not changed);changed=True\n",'')
    s=replace(s,"save('new-runtime.private',dropin)","save('runtime-before.private',dropin)")
    ast.parse(s);return s


RETIRE_EXTRA=r'''
RUNTIME=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
NAME='pg1160-once-resume.conf';MORNING='schubert-nk-morning-controller.service'
def runtime_configuration():return {u:show(u,configuration_fields())for u in UNITS}
def require_runtime_configuration(actual):
 require(set(actual)==set(baseline['configuration']))
 for unit,old in baseline['configuration'].items():
  new=actual[unit];require(set(new)==set(old))
  exclusions={'DropInPaths'}if changed and unit==MORNING else set()
  require(all(new[k]==old[k]for k in old.keys()-exclusions))
  if changed and unit==MORNING:require(new['DropInPaths']==' '.join(p for p in old['DropInPaths'].split()if p!=str(RUNTIME/NAME)))
def runtime_tree():return tree(pathlib.Path('/run/systemd/system'))
def require_runtime_tree_initial():
 require(runtime_tree()==baseline['runtime'])
 require(metadata(RUNTIME)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and {p.name for p in RUNTIME.iterdir()}=={NAME})
 p=RUNTIME/NAME;require(metadata(p)[2:7]==[0,0,stat.S_IFREG|0o644,1,647]and hashlib.sha256(p.read_bytes()).hexdigest()=='d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0')
def require_runtime_tree():
 if not changed:require(runtime_tree()==baseline['runtime']);return
 expected=baseline['runtime'];actual=runtime_tree();require(set(actual)==set(expected)-{str(RUNTIME/NAME)})
 for p,value in expected.items():
  if p==str(RUNTIME/NAME):continue
  if p==str(RUNTIME):
   a=actual[p];require(a['sha256']==value['sha256']and a['metadata'][:6]==value['metadata'][:6]and a['metadata'][7]>=value['metadata'][7]and a['metadata'][8]>=value['metadata'][8])
  else:require(actual[p]==value)
 require(not list(RUNTIME.iterdir()))
'''


def files():
    from pathlib import Path
    root=Path(__file__).resolve().parent
    return {'Pg1166WrongRuntimeRetirement.java':java(),'pg1166_wrong_runtime_refs.py':refs(),
            'Pg1166WrongRuntimeEntry.java':(root/'Pg1166WrongRuntimeEntry.java').read_text(),
            'Pg1166WrongRuntimeEntryTest.java':(root/'Pg1166WrongRuntimeEntryTest.java').read_text()}
