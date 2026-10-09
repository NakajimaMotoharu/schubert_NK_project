"""BUG960 exact pre-freeze owner handoff; no publication, business Unit stop or recovery replay."""
import ast
import inspect
from pg801_guard_handoff import payload as previous
import pg784_stopped_baseline as transport
CORRECTION=r'''
h.PARENT='7ea672e8a76c4a4a8a7994652366a4cc'
definitions=ast.parse((base/'pg835-pending-tools-v1/pg835_snapshot.py').read_text())
for name in ('parent_value','configuration'):
 node=next(n for n in definitions.body if isinstance(n,ast.FunctionDef)and n.name==name)
 source=ast.unparse(node).replace("'137240785885'","'155954641282'").replace('accepted(old, new, show(unit), {})',"accepted(old,new,show(unit),baseline()['units'][unit])")
 exec(compile(source,'<fixed samecurrent readonly cohort>','exec'),h.__dict__)
'''
def payload():
    raw=previous().replace('pg801-guard-handoff-v1','pg836-pre-freeze-handoff-v1')
    raw='import ast\n'+raw
    raw=raw.replace('pg799','pg835').replace('Pg799','Pg835').replace('0.1.0-PG750','0.1.0-PG796')
    raw=raw.replace('3112232','3412116').replace('15308543','16855351')
    raw=raw.replace('102cdf1d365ab321f74b523237590eee764ae858','2a0d5aa392c85a1dc12a1cdb423978e8500895b8')
    raw=raw.replace('c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977')
    raw=raw.replace("and not(p/'task'/str(pid)/'children').read_text().strip()", "and all(not(task/'children').read_text().strip()for task in(p/'task').iterdir())")
    raw=raw.replace('h.load_definitions()\n','h.load_definitions()\n'+CORRECTION+'\n')
    raw=raw.replace("'batchRows':544,'startupEntries':39", "'batchRows':554,'startupEntries':43")
    ast.parse(raw);return raw
if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg836-pre-freeze-handoff-v1')
    context={**transport.__dict__,'PAYLOAD':payload()}
    exec(compile(raw,'<836 exact pre-freeze failed owner>','exec'),context);context['main']()
