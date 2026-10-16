"""BUG1344 current data-only observation under ten real references; no declaration acceptance."""
from contextlib import contextmanager
import inspect
import pg4212_quiescent_configuration_observation as previous
from pg4060_original_profile_dual_stack import once

SLOT='pg4214-quiescent-ten-ref-observation-v1'


@contextmanager
def metadata_refs(manager,bus,names):
    held=[]
    try:
        for unit in names:
            manager.LoadUnit(unit);manager.RefUnit(unit);held.append(unit)
        yield
    finally:
        try:
            for unit in reversed(held):manager.UnrefUnit(unit)
        finally:bus.close()


def payload():
    raw=previous.payload().replace(previous.SLOT,SLOT)
    start=raw.index('signed={};exec(SIGNED_SOURCE,signed)')
    final="(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))"
    raw=once(raw,final,'')
    prefix=raw[:start];body=raw[start:]
    prefix+='\nfrom contextlib import contextmanager\nimport dbus\n'+inspect.getsource(metadata_refs)+'\n'
    prefix+="bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')\n"
    return prefix+"with metadata_refs(manager,bus,tuple(old['units'])):\n"+''.join(' '+line+'\n'for line in body.splitlines())+"\nvalue['newTenMetadataRefsNormalClose']=True\n"+final+'\n'


def main():
    ns={**vars(__import__('pg4210_quiescent_current_read')),'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(ns['main']),'<ten real references observation>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
