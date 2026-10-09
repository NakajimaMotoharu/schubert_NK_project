"""New-only current owners plus full fixed32 union; previous27 snapshot preserved."""
import inspect
import pg784_stopped_baseline as transport
from pg852_current_capture import payload
from pg847_configuration import FIELDS
if __name__=='__main__':
    raw=payload().replace('pg852-doneafter-timeout-v1','pg855-doneafter-current-v2')
    marker='h.load_definitions();old=h.baseline();'
    assert raw.count(marker)==1
    raw=raw.replace(marker,'h.load_definitions();h.FIELDS_CONFIGURATION=frozenset('+repr(sorted(FIELDS))+');old=h.baseline();')
    entry=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg855-doneafter-current-v2')
    context={**transport.__dict__,'PAYLOAD':raw}
    exec(compile(entry,'<855v2 current full32 capture only>', 'exec'),context)
    context['main']()
