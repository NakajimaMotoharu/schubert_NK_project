"""Independent genuine new resource source terminal; no lifecycle authority."""
import inspect
import pg2544_strict_current_terminal as previous
from pg2674_operation_publication_sources import production,candidate_bom

SOURCE=production();SLOT='pg2700-operation-current-terminal-v1'


def payload(binding,bom=None):
    if bom is None:bom=candidate_bom()
    if binding.get('run')=='b29fb3e5-2c46-4eac-b8f3-d03b986338e3'or binding.get('activation')=='d0219581-24e4-4136-ac90-39d54e704378':raise ValueError('historical a79 completion is not new candidate')
    raw=previous.payload(binding,bom).replace(previous.SLOT,SLOT).replace('PG2512','PG2654').replace(previous.SOURCE,SOURCE)
    compile(raw,'<new resource genuine terminal>','exec');return raw


def entry():
    raw=inspect.getsource(previous.entry).replace('pg2542-strict-current-live-binding-v1','pg2686-operation-current-live-binding-v1').replace('pg2538-parent-watch-v1','pg2682-parent-watch-v1')
    ns={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new independent terminal entry>','exec'),ns);return ns['entry']()


if __name__=='__main__':raise SystemExit(entry()())
