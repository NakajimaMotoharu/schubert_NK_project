"""BUG1207/YKT975: exact current native-augmented start schema, all prior fields and SHA retained."""
import inspect
from pyflakes.api import check
import pg2081_current_newrun_full_live_seal as previous

SLOT='pg2085-native-augmented-newrun-full-seal-v1'


def before_shape(before):
    return (type(before)is dict and set(before)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native'}and type(before['native'])is dict and bool(before['native']))


def payload(binding):
    raw=previous.payload(binding).replace(previous.SLOT,SLOT)
    old="require(set(before)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'})"
    if raw.count(old)!=1:raise ValueError('one exact current start schema boundary required')
    raw=raw.replace(old,inspect.getsource(before_shape)+'\nrequire(before_shape(before))',1)
    if check(raw,'<actual native augmented newrun fullseal>'):raise ValueError('all whole fullseal globals required')
    compile(raw,'<current native augmented fullseal>','exec');return raw


def entry():
    raw=inspect.getsource(previous.entry).replace('def entry():','def current_entry():',1)
    ns={**previous.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new fullseal immutable entry>','exec'),ns);return ns['current_entry']()


if __name__=='__main__':raise SystemExit(entry()())
