"""Fresh readonly same-generation capture before completed-failed recovery; no action replay."""
import inspect
import pg784_stopped_baseline as transport
from pg852_current_capture import payload
if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg855-doneafter-current-v1')
    context={**transport.__dict__,'PAYLOAD':payload().replace('pg852-doneafter-timeout-v1','pg855-doneafter-current-v1')}
    exec(compile(raw,'<855 current owner reread before normal recovery>','exec'),context)
    context['main']()
