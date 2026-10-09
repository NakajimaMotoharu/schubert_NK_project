"""New capture; prove omitted empty ExecStop through real PID1 typed property, no fallback."""
from pathlib import Path
from pg662_sources import replace
from pg775_failure_full import source as prior

R=Path(__file__).resolve().parent

ADDITIONAL=r'''
def complete_configuration(raw,unit):
 if not isinstance(raw,str):raise ValueError('configuration type refused')
 keys=[line.split('=',1)[0]for line in raw.splitlines()]
 if 'ExecStop'in keys:return configuration_value(raw)
 import dbus
 bus=dbus.SystemBus(private=True)
 try:
  manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
  path=manager.GetUnit(unit)
  properties=dbus.Interface(bus.get_object('org.freedesktop.systemd1',path),'org.freedesktop.DBus.Properties').GetAll('org.freedesktop.systemd1.Service')
  stop=properties['ExecStop']
  if not isinstance(stop,dbus.Array)or str(stop.signature)!='(sasbttttuii)'or len(stop)!=0:raise ValueError('actual empty ExecStop refused')
 finally:bus.close()
 return configuration_value(raw+'ExecStop=\n')
'''


def source():
    return replace(prior().replace('pg775-failure-full758-v1','pg776-failure-full758-v1'),
        (('def configurations():',ADDITIONAL+'\ndef configurations():'),
         ("configuration_value(command(['/usr/bin/systemctl','show',u,'--property='+fields]).decode())","complete_configuration(command(['/usr/bin/systemctl','show',u,'--property='+fields]).decode(),u)")))


if __name__=='__main__':
    exec(compile(source(),'<new776 full failed capture>','exec'),{'__file__':str(R/'pg776_failure_full.py'),'__name__':'__main__'})
