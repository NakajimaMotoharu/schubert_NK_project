"""BUG977: typed inactive Unit property while owning its same-bus Ref."""
import ast,subprocess,sys
from pathlib import Path
from pg863_stage_candidate_v4 import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous().replace('pg863-stage-v4','pg863-stage-v5').replace('pg863-release-v4.tar','pg863-release-v5.tar').replace('pg863-candidate-stage-v4','pg863-candidate-stage-v5')
    raw=raw.replace('path=manager.GetUnit(unit)','path=manager.LoadUnit(unit);manager.RefUnit(unit)')
    raw=raw.replace('finally:bus.close()','finally:\n  try:manager.UnrefUnit(unit)\n  finally:bus.close()')
    ast.parse(raw);return raw
def preflight():
    tree=ast.parse(source());payload=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
    payload=payload[:payload.index("root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')")]
    payload+='\nassert not os.path.lexists("/opt/schubert-nk/releases/0.1.0-PG862") and not os.path.lexists("/var/lib/pgpt-s1-preservation/pg862-manifest.sig")\nprint("STAGE863_PREFLIGHT full24-564/all32/alltrees/runtimeEmpty/tenStopped PASS mutation0")\n'
    p=Path('/home/mini/codex/project1/work/pgpt-vm/private')
    cmd=['ssh','-i',str(p/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(p/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    subprocess.run(cmd,input=payload.encode(),check=True)
if __name__=='__main__':
    if sys.argv[1:]==['preflight']:preflight()
    else:
        assert not sys.argv[1:]
        namespace={'__file__':str(R/'pg863_stage_candidate_v5.py'),'__name__':'new_only_unused_signed862_v5'}
        exec(compile(source(),'<863 typed reference v5>','exec'),namespace);namespace['main']()
