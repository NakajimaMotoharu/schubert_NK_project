"""Same-day new-run independent terminal, all24 rows and whole live seal."""
import inspect
import sys
import types
from pyflakes.api import check
import pg2700_operation_current_terminal as old_terminal
import pg2702_operation_current_rows as old_rows
import pg2704_operation_current_full_seal as old_seal
import pg2079_current_same_day_rows_capture as row_template
from pg3798_hygiene_current_observer import SOURCE,BOM
from pg3802_hygiene_current_noargs_once import SLOT as ONCE
from pg3804_hygiene_current_live_binding import SLOT as LIVE
from pg3806_hygiene_admission_before import before
from pg3788_hygiene_publication_sources import BOOT

TERM='pg3808-hygiene-current-terminal-v1';ROWS='pg3810-hygiene-current-rows-v1';SEAL='pg3812-hygiene-current-full-seal-v1'


def bind(raw):
    for a,b in [('PG2654','PG3748'),('pg2654-manifest.sig','pg3748-manifest.sig'),('b2d6f605-61cf-425f-8fbd-12d606f6ee66',BOOT),('b2d6f60561cf425f8fbd12d606f6ee66',BOOT.replace('-','')),('pg2686-operation-current-live-binding-v1',LIVE),('pg2684-operation-current-noargs-once-v2',ONCE),('pg2682-parent-watch-v1','pg3798-parent-watch-v1'),(old_terminal.SOURCE,SOURCE),(old_terminal.SLOT,TERM),(old_rows.SLOT,ROWS),(old_seal.SLOT,SEAL)]:raw=raw.replace(a,b)
    return raw


def terminal_payload(binding):return bind(old_terminal.payload(binding,BOM))


def rows_payload():
    raw=inspect.getsource(row_template.payload)
    for a,b in [('pg2074-current-newrun-live-binding-v1',LIVE),('pg2072-current-noargs-newrun-once-v1',ONCE),('796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05',before()),('pg2079-current-same-day-rows-capture-v1',ROWS),('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT)]:raw=raw.replace(a,b)
    values={**row_template.__dict__,'transport':types.SimpleNamespace(SOURCE=SOURCE)}
    exec(compile(raw,'<new same-day independent all24 factory>','exec'),values)
    result=values['payload']()
    marker='sql="begin isolation level repeatable read read only;'
    guard="release=pathlib.Path('/opt/schubert-nk/current');approved_raw=(release/'RELEASE-MANIFEST.json').read_bytes();require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG3748'and hashlib.sha256(approved_raw).hexdigest()==BOM and json.loads(approved_raw)['source']['commit']==SOURCE)\n"
    if result.count(marker)!=1:raise ValueError('one independent SQL snapshot boundary')
    result='SOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\n'+result.replace(marker,guard+marker)
    result=result.replace("print(json.dumps({**result,'actualExit':0,","require((release/'RELEASE-MANIFEST.json').read_bytes()==approved_raw and str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG3748')\nprint(json.dumps({**result,'actualExit':0,")
    if check(result,'<new same-day all24>'):raise ValueError('all24 complete namespace required')
    compile(result,'<actual same-day newrun full24 oracle>','exec');return result


def seal_payload(binding):
    function=types.FunctionType(old_seal.payload.__code__,{**old_seal.__dict__,'SOURCE':SOURCE,'SLOT':SEAL,'TERM':TERM,'before':before,'terminal':lambda b,bom:terminal_payload(b)})
    raw=bind(function(binding,BOM))
    if check(raw,'<whole actual same-day newrun seal>'):raise ValueError('whole same-source namespace required')
    compile(raw,'<new7fff whole same-day newrun seal>','exec');return raw


def entry(phase):
    modules={'terminal':(old_terminal,TERM,terminal_payload),'rows':(old_rows,ROWS,rows_payload),'seal':(old_seal,SEAL,seal_payload)}
    if phase not in modules:raise ValueError('explicit terminal/rows/seal only')
    module,slot,payload=modules[phase];raw=inspect.getsource(module.entry)
    for a,b in [('pg2686-operation-current-live-binding-v1',LIVE),('pg2682-parent-watch-v1','pg3798-parent-watch-v1'),('pg2702-operation-current-rows-v1',ROWS),('pg2700-operation-current-terminal-v1',TERM)]:raw=raw.replace(a,b)
    values={**module.__dict__,'SOURCE':SOURCE,'SLOT':slot,'TERM':TERM,'payload':payload}
    exec(compile(raw,'<independent newsource phase transport>','exec'),values);return values['entry']()


if __name__=='__main__':raise SystemExit(entry(sys.argv[1])())
