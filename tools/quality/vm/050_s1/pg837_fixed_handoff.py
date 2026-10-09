"""New-only after836 pre-signal missing import; old836 failure is not overwritten."""
import inspect
from pg836_fixed_handoff import payload
import pg784_stopped_baseline as transport
if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg837-pre-freeze-handoff-v1')
    context={**transport.__dict__,'PAYLOAD':payload().replace('pg836-pre-freeze-handoff-v1','pg837-pre-freeze-handoff-v1')}
    exec(compile(raw,'<837 new-only fixed import>', 'exec'),context);context['main']()
