"""BUG966: only fresh post, exact current epoch; never re-publish candidate."""
import ast,inspect
import pg784_stopped_baseline as transport
from pg840_candidate_post import PAYLOAD as previous

def payload():
 raw=previous.replace('pg840-current832-post-v1','pg840-current832-post-v2')
 marker='h.load_definitions();probe='
 assert raw.count(marker)==1
 raw=raw.replace(marker,"h.load_definitions();\nimport inspect\nepoch_source=inspect.getsource(h.epoch_value).replace('e9f11f1c-f087-458a-aad0-8c1e4e140571','0eece14c-f832-47c2-b7dd-14125682e7ea')\nexec(compile(epoch_source,'<fixed current0ee strict epoch>','exec'),h.__dict__)\nprobe=")
 ast.parse(raw);return raw

if __name__=='__main__':
 raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg840-current832-post-v2');context={**transport.__dict__,'PAYLOAD':payload()}
 exec(compile(raw,'<840 fresh v2 strict0ee>', 'exec'),context);context['main']()
