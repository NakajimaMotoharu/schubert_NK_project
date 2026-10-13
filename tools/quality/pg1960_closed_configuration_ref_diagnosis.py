"""Closed diagnostic holds all ten real Unit references through both fresh reads."""
import inspect
import pg1955_closed_reload_configuration_diagnosis as prior
from pg1947_reload_configuration_delta import payload as original

SLOT='pg1960-closed-configuration-ref-diagnosis-v1'


def payload():
    raw=original();start=raw.index('changed={};states={}')
    prefix=raw[:start];body=raw[start:]
    scope="""
import dbus
UNITS=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
"""
    return prefix+scope+'\n'.join(' '+line for line in body.splitlines())+"\nfinally:\n for unit in reversed(refs):manager.UnrefUnit(unit)\n bus.close()\n"


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<closed allRef diagnostic>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
