"""947 correction: authenticate current796, not stale prepublication750; no replay."""
import ast
import inspect
import pg784_stopped_baseline as transport
from pg803_published_handoff import payload as previous

PARENT=r'''def current_parent():
 h.require(h.parent_value(h.show(h.EXTRA[0]))and not pathlib.Path('/proc/2797579').exists());h.kernel_empty(h.EXTRA[0])
 h.require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'and pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796'))
 h.require(hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d')
h.parent=current_parent
'''

def payload():
 raw=previous().replace('pg803-published-handoff-v1','pg803-published-handoff-v2');marker='h.load_definitions()\n';assert raw.count(marker)==1
 return raw.replace(marker,marker+PARENT)

if __name__=='__main__':
 ast.parse(payload());raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg803-published-handoff-v2');context={**transport.__dict__,'PAYLOAD':payload()}
 exec(compile(raw,'<803-v2 fixed newcurrent guard known handoff>', 'exec'),context);context['main']()
