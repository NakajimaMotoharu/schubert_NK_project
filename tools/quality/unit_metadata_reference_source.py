"""Existing finite LoadUnit/RefUnit contract, no start/reload/config write; close before success output."""


def scope(body):
    return """import dbus
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in expected['units']:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
"""+'\n'.join(' '+line if line else line for line in body.splitlines())+"""
finally:
 try:
  for unit in reversed(refs):manager.UnrefUnit(unit)
 finally:bus.close()
"""
