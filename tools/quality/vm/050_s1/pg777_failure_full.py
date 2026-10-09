"""Fresh readonly all24 capture with ten retained Unit references, never worker start."""
import ast
from pathlib import Path
from pg776_failure_full import source as prior

R=Path(__file__).resolve().parent

REFERENCE=r'''
import dbus
class CaptureReferences:
 units=('schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service','artemis.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','schubert-nk-bootstrap-admin.service')
 def __enter__(self):
  self.bus=dbus.SystemBus(private=True);self.refs=[]
  try:
   daemon=dbus.Interface(self.bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
   assert int(daemon.GetConnectionUnixProcessID('org.freedesktop.systemd1'))==1 and int(daemon.GetConnectionUnixUser('org.freedesktop.systemd1'))==0
   self.manager=dbus.Interface(self.bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
   for unit in self.units:
    path=self.manager.LoadUnit(unit);self.manager.RefUnit(unit);self.refs.append(unit)
    assert path==self.manager.GetUnit(unit)
  except BaseException:
   for unit in reversed(self.refs):self.manager.UnrefUnit(unit)
   self.bus.close();raise
  return self
 def __exit__(self,kind,value,traceback):
  for unit in reversed(self.refs):self.manager.UnrefUnit(unit)
  self.bus.close()
'''


def source():
    raw=prior().replace('pg776-failure-full758-v1','pg777-failure-full758-v1')
    tree=ast.parse(raw)
    node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
    p=ast.literal_eval(node.value);marker="base=pathlib.Path('/var/lib/pgpt-s1-preservation');";assert p.count(marker)==1
    index=p.index(marker);p=p[:index]+REFERENCE+'\nwith CaptureReferences():\n'+''.join(' '+line+'\n'for line in p[index:].splitlines())
    # Replace only the literal, not the operator source/host guard.
    lines=raw.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+ 'PAYLOAD='+repr(p)+'\n'+''.join(lines[node.end_lineno:])


if __name__=='__main__':
    exec(compile(source(),'<new777 tenref full private capture>','exec'),{'__file__':str(R/'pg777_failure_full.py'),'__name__':'__main__'})
