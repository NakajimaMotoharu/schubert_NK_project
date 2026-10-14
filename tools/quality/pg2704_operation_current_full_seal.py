"""Whole new resource source/run seal; terminal/all24/four owned ordinary peers."""
import inspect
from pyflakes.api import check
import pg2548_strict_current_full_seal as previous
from pg2700_operation_current_terminal import payload as terminal,SLOT as TERM
from pg2698_operation_admission_before import before
from pg2674_operation_publication_sources import production,candidate_bom

SOURCE=production();SLOT='pg2704-operation-current-full-seal-v1'


def payload(binding,bom=None):
    if bom is None:bom=candidate_bom()
    raw=previous.payload(binding,bom)
    for a,b in [(previous.SLOT,SLOT),('pg2540-strict-current-noargs-once-v1','pg2684-operation-current-noargs-once-v2'),
      (previous.BEFORE,before()),(previous.SOURCE,SOURCE),('PG2512','PG2654'),('pg2512-manifest.sig','pg2654-manifest.sig')]:raw=raw.replace(a,b)
    guard=terminal(binding,bom);marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+TERM+"')"
    if guard.count(marker)!=1:raise ValueError('one actual new terminal scope required')
    raw=previous.previous.prior.prior.previous.previous.constant(raw,'GUARD',guard[:guard.index(marker)])
    if check(raw,'<whole new current seal>'):raise ValueError('complete independent seal namespace required')
    compile(raw,'<new resource whole seal>','exec');return raw


def entry():
    raw=inspect.getsource(previous.entry)
    for a,b in [('pg2544-strict-current-terminal-v1',TERM),('pg2546-strict-current-rows-v1','pg2702-operation-current-rows-v1'),('pg2542-strict-current-live-binding-v1','pg2686-operation-current-live-binding-v1')]:raw=raw.replace(a,b)
    ns={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'TERM':TERM,'payload':payload}
    exec(compile(raw,'<new current whole independent capture>','exec'),ns);return ns['entry']()


if __name__=='__main__':raise SystemExit(entry()())
