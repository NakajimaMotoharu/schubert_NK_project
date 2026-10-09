"""BUG978: hold all ten Unit references before any configuration observation."""
import ast,sys,subprocess
from pathlib import Path
import pg863_stage_candidate_v5 as prior
R=Path(__file__).resolve().parent
REFS='''
import dbus
class StageReferences:
 def __enter__(self):
  self.bus=dbus.SystemBus(private=True);self.held=[]
  self.manager=dbus.Interface(self.bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
  for unit in ('caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service'):
   self.manager.LoadUnit(unit);self.manager.RefUnit(unit);self.held.append(unit)
  return self
 def __exit__(self,*args):
  for unit in reversed(self.held):self.manager.UnrefUnit(unit)
  self.bus.close()
'''
def source():
    raw=prior.source().replace('pg863-stage-v5','pg863-stage-v6').replace('pg863-release-v5.tar','pg863-release-v6.tar').replace('pg863-candidate-stage-v5','pg863-candidate-stage-v6')
    tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets));body=node.value.value
    imports,rest=body.split('assert os.geteuid()==0',1)
    body=imports+REFS+'\nwith StageReferences():\n'+''.join(' '+l+'\n'for l in ('assert os.geteuid()==0'+rest).splitlines())
    ast.parse(body)
    lines=raw.splitlines(keepends=True);raw=''.join(lines[:node.lineno-1])+'PAYLOAD='+repr(body)+'\n'+''.join(lines[node.end_lineno:]);ast.parse(raw);return raw
if __name__=='__main__':
    if sys.argv[1:]==['preflight']:
        tree=ast.parse(source());payload=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        payload=payload[:payload.index(" root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')")]
        payload+=' assert not os.path.lexists("/opt/schubert-nk/releases/0.1.0-PG862") and not os.path.lexists("/var/lib/pgpt-s1-preservation/pg862-manifest.sig")\nprint("STAGE863_PREFLIGHT full24-564/all32/alltrees/runtimeEmpty/tenStopped/tenRefsClosed PASS mutation0")\n'
        p=Path('/home/mini/codex/project1/work/pgpt-vm/private')
        cmd=['ssh','-i',str(p/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(p/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
        subprocess.run(cmd,input=payload.encode(),check=True)
    else:
        assert not sys.argv[1:]
        namespace={'__file__':str(R/'pg863_stage_candidate_v6.py'),'__name__':'new_only_unused_signed862_v6'}
        exec(compile(source(),'<863 all ten reference v6>','exec'),namespace);namespace['main']()
