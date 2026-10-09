"""BUG964: exact v4 pre-DB owner only; keep failed 143/UNKNOWN, no Unit mutation."""
import ast
import inspect
from pg836_fixed_handoff import payload as previous
import pg784_stopped_baseline as transport

def payload():
    raw=previous().replace('pg836-pre-freeze-handoff-v1','pg839-pre-db-v4-handoff-v1')
    raw=raw.replace('pg835-pending-tools-v1','pg835-pending-tools-v4')
    raw=raw.replace('pg835-pending-codeonly','pg835-pending-codeonly-v4')
    raw=raw.replace('3412116','3413933').replace('16855351','17029042')
    marker="argv=(p/'cmdline').read_bytes();"
    assert raw.count(marker)==1
    raw=raw.replace(marker,marker+"assert hashlib.sha256(argv).hexdigest()=='b84faa0ed6b06264ed2609e37c6f2d691713e42e75e29c6806f6e75751114f07';")
    ast.parse(raw);return raw

if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg839-pre-db-v4-handoff-v1')
    context={**transport.__dict__,'PAYLOAD':payload()}
    exec(compile(raw,'<839 exact v4 preDB owner>', 'exec'),context);context['main']()
