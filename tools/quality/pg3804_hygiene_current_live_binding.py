"""Read-only actual new Root/peer identity; no start or budget extension."""
import inspect
from pyflakes.api import check
import pg3466_outbox_current_live_binding as previous
from pg3798_hygiene_current_observer import SOURCE, BOM
from pg3802_hygiene_current_noargs_once import SLOT as ONCE
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
from pg3756_hygiene_unused_sources import current_tuple

SLOT='pg3804-hygiene-current-live-binding-v1'


def body():
    raw=previous.body().replace('PG3420','PG3748')
    current,_,_=current_tuple()
    raw+='\nrequire(fields[1]!='+repr(current['run'])+'and fields[3]!='+repr(current['activation'])+')\n'
    if check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n'+raw,'<actual new Root binding>'):raise ValueError('whole actual live namespace required')
    compile(raw,'<new7fff Root distinct from prior4856>','exec');return raw


def main():
    raw=inspect.getsource(previous.transport.main).replace('pg2015-completed-run-fresh-resume-once-v1',ONCE)
    values={**previous.transport.__dict__,'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'body':body}
    exec(compile(raw,'<actual once-issued job observer>','exec'),values)
    with management_gate(P/'current-management-critical.lock'):return values['main']()


if __name__=='__main__':raise SystemExit(main())
