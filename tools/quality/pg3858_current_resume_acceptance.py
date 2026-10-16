"""Independent current completed-resume terminal, all24 oracle, and full live seal."""
import inspect
import json
import sys
import types
from pyflakes.api import check
import pg3582_current_browser_acceptance as previous
import pg3808_hygiene_acceptance as current
from pg3854_current_completed_resume_once import SLOT as ONCE
from pg3856_current_resume_live_binding import SLOT as LIVE
from pg3844_current_resume_sources import SOURCE,BOM,BOOT,RUN
from pg1446_current_cold_stage import W

TERM='pg3858-current-resume-terminal-v1'
ROWS='pg3860-current-resume-rows-v1'
SEAL='pg3862-current-resume-full-seal-v1'


def before():
    value=json.loads((W/'pg3850-current-resume-independent-post-v1/manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['source']!=SOURCE or not value['result']['independentResumeOnlyDeltaVerified']:
        raise ValueError('actual current prepared full11 required')
    return value['result']['preparedAfterSha256']


def live():
    value=json.loads((W/LIVE/'manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['productionSource']!=SOURCE or value['binding']['run']!=RUN or value['binding']['activation']=='e7584da8-7f80-4f8e-a46c-f46b2388e773':
        raise ValueError('current same-run genuinely new activation required')
    return value


def bind(raw):
    for a,b in [(previous.previous.TERM,TERM),(previous.previous.ROWS,ROWS),(previous.previous.SEAL,SEAL),
                (previous.previous.ONCE,ONCE),(previous.previous.LIVE,LIVE),('pg3462-parent-watch-v1','pg3852-parent-watch-v1'),
                (previous.SOURCE,SOURCE),('PG3420','PG3748'),('pg3420-manifest.sig','pg3748-manifest.sig')]:raw=raw.replace(a,b)
    return raw


def terminal_payload(binding):return current.terminal_payload(binding).replace(current.TERM,TERM)


def oracle_source():return previous.oracle_source()


def values():
    return {**previous.__dict__,'SOURCE':SOURCE,'BOM':BOM,'BOOT':BOOT,'RUN':RUN,
        'ONCE':ONCE,'LIVE':LIVE,'TERM':TERM,'ROWS':ROWS,'SEAL':SEAL,'BEFORE':before(),
        'live':live,'bind':bind,'terminal_payload':terminal_payload,'oracle_source':oracle_source}


def rows_payload():
    raw=types.FunctionType(previous.rows_payload.__code__,values())()
    marker='sql="begin isolation level repeatable read read only;'
    guard="release=pathlib.Path('/opt/schubert-nk/current');approved=(release/'RELEASE-MANIFEST.json').read_bytes();require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG3748'and hashlib.sha256(approved).hexdigest()==BOM and json.loads(approved)['source']['commit']==SOURCE)\n"
    if raw.count(marker)!=1:raise ValueError('one independent all24 read boundary')
    raw='SOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\n'+raw.replace(marker,guard+marker)
    if check(raw,'<current resume independent all24>'):raise ValueError('complete all24 namespace')
    compile(raw,'<current same-run all24 oracle>','exec');return raw


def seal_payload(binding):return types.FunctionType(previous.seal_payload.__code__,values())(binding)


def entry(phase):
    roles={'terminal':(current.old_terminal,TERM,terminal_payload),'rows':(current.old_rows,ROWS,rows_payload),'seal':(current.old_seal,SEAL,seal_payload)}
    if phase not in roles:raise ValueError('explicit terminal/rows/seal only')
    module,slot,payload=roles[phase];raw=inspect.getsource(module.entry)
    for a,b in [('pg2686-operation-current-live-binding-v1',LIVE),('pg2682-parent-watch-v1','pg3852-parent-watch-v1'),('pg2702-operation-current-rows-v1',ROWS),('pg2700-operation-current-terminal-v1',TERM)]:raw=raw.replace(a,b)
    ns={**module.__dict__,'SOURCE':SOURCE,'SLOT':slot,'TERM':TERM,'payload':payload}
    exec(compile(raw,'<current resume independent phase transport>','exec'),ns);return ns['entry']()


if __name__=='__main__':raise SystemExit(entry(sys.argv[1])())
