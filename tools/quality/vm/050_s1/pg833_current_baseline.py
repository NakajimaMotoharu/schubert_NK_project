"""Fresh read-only same-current reauthentication before new signed code-only; no replay."""
import ast
import inspect
from pg816_retirement_post import payload as prior
import pg784_stopped_baseline as transport
def payload():
    raw=prior()
    assert raw.count("save=base/'pg816-runtime-retired-post-v1'")==1
    raw=raw.replace("save=base/'pg816-runtime-retired-post-v1'","save=base/'pg833-current-before832-v1'")
    ast.parse(raw);return raw
if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg833-current-before832-v1')
    context={**transport.__dict__,'PAYLOAD':payload()}
    exec(compile(raw,'<833 fresh readonly before new candidate>', 'exec'),context);context['main']()
