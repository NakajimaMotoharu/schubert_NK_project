"""Independent SS full24 same-day oracle bound to current source/run before."""
import inspect
import types
import pg2079_current_same_day_rows_capture as prior
from pg2176_newsource_normal_observer import SOURCE

SLOT='pg2184-newsource-same-day-rows-v1'
BEFORE='01d3dde37039d7b9dff2f3a1261185ef186f756c6f870e6ef2080663b1c846a1'


def payload():
    raw=inspect.getsource(prior.payload)
    for old,new in [('pg2074-current-newrun-live-binding-v1','pg2180-newsource-live-binding-v1'),('pg2072-current-noargs-newrun-once-v1','pg2178-newsource-noargs-once-v1'),('796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05',BEFORE),('pg2079-current-same-day-rows-capture-v1',SLOT)]:raw=raw.replace(old,new)
    ns={**prior.__dict__,'transport':types.SimpleNamespace(SOURCE=SOURCE)}
    exec(compile(raw,'<current newsource all24 independent rows>','exec'),ns);return ns['payload']()


def entry():
    raw=inspect.getsource(prior.transport.main).replace('pg2021-fresh-resume-terminal-receipt-v1','pg2182-newsource-terminal-receipt-v1')
    ns={**prior.transport.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<newsource same-day rows entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
