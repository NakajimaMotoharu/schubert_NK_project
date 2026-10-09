"""Independent actual runtime841 retired: compare both operator after and trusted859 before."""
import ast,inspect
from pathlib import Path
import pg784_stopped_baseline as transport
from pg816_retirement_post import payload as previous
from pg860_retirement import bind
AFTER='4bd686da5660104c6dc6975baa468fd80a015e5ecfcc3896fc26b4f9e2147579'
BEFORE='ba0ec596c2800f4403f04c545869e2bbe500bd14c6706e4dc2ae4fa9c1a5b2fd'
def payload():
    raw=bind(previous()).replace('pg816-runtime-retired-post-v1','pg861-runtime841-retired-post-v1')
    raw=raw.replace('d725011754d5a06d8591b16820b9e272aa41116723df8d6946384d6d1bc13652',AFTER)
    raw=raw.replace('==43','==47').replace("'startupEntries':43","'startupEntries':47").replace("'batchRows':554","'batchRows':564")
    # No intent existed; neither stop nor runtime retirement may remove an original entry.
    raw=raw.replace("set(before['trees'][startup])-{intent}","set(before['trees'][startup])")
    marker='with CaptureReferences():\n value=snapshot();assert value==snapshot()'
    assert raw.count(marker)==1
    extra='''with CaptureReferences():
 value=snapshot();assert value==snapshot()
 original_bytes=(base/'pg859-completed-failed-post-v1/after.private.json').read_bytes()
 assert hashlib.sha256(original_bytes).hexdigest()=='''+repr(BEFORE)+'''
 original=json.loads(original_bytes)
 assert value['rows']==original['rows'] and value['trees']==original['trees']
 removed='/run/systemd/system/schubert-nk-morning-controller.service.d/pg841-once-resume.conf'
 assert value['unitFiles']=={k:v for k,v in original['unitFiles'].items()if k!=removed}
'''
    raw=raw.replace(marker,extra);ast.parse(raw);return raw
if __name__=='__main__':
    entry=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg861-runtime841-retired-post-v1')
    namespace={**transport.__dict__,'PAYLOAD':payload()}
    exec(compile(entry,'<861 independent actual current and original before>','exec'),namespace);namespace['main']()
