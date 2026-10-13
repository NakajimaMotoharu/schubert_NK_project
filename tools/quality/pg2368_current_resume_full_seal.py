"""Current same-source terminal/rows/four-owner seal from fixed explicit-resume admission."""
import inspect
from pyflakes.api import check
import pg2186_newsource_full_live_seal as previous
from pg2025_fresh_resume_full_live_seal import constant
from pg2364_current_resume_terminal import payload as terminal_payload,SLOT as TERM
from pg2366_current_resume_rows import oracle_source
from pg2360_current_completed_resume_once import SOURCE,BOM,RUN,BEFORE

SLOT='pg2368-current-resume-full-seal-v1'


def payload(binding):
    raw=previous.payload(binding)
    for a,b in [(previous.SLOT,SLOT),('pg2178-newsource-noargs-once-v1','pg2360-current-completed-resume-once-v1'),(previous.BEFORE,BEFORE),('3d69f5af-6bac-46b1-a540-7591c4a79a0d','b2d6f605-61cf-425f-8fbd-12d606f6ee66'),('2026-10-13T06:29:34.698736Z','2026-10-13T15:01:53.237266Z'),('02bddddf-9cd3-4668-9d67-7561232fc4e4',RUN),('20b86040-ffd5-4d17-9fca-5d83048ba905',binding['activation'])]:raw=raw.replace(a,b)
    marker="require(before_shape(before))"
    if raw.count(marker)!=1:raise ValueError('one current full admission shape required')
    # This normal verifier stores native in its separately sealed post envelope,
    # rather than changing the ten-field management snapshot dialect.
    guard="""require(type(before)is dict and set(before)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'})
native_post_raw=(BASE/'pg2356-current-runtime-verification-post-v1/after.private.json').read_bytes()
require(hashlib.sha256(native_post_raw).hexdigest()=='60bfaf9b2f28277088bcea565d920a6cd495914a58cf8ce9d6c90fe28f9045af')
native_post=json.loads(native_post_raw);require(before==native_post['before'])
before['native']=native_post['native'];require(before_shape(before))"""
    raw=raw.replace(marker,guard)
    terminal=terminal_payload(binding);point="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+TERM+"')"
    raw=constant(raw,'GUARD',terminal[:terminal.index(point)])
    oracle=oracle_source().replace('def qualify(old,new,run,cutoff,lower,upper):','def qualify_resume(old,new,run,cutoff,lower,upper):')
    oracle+="\ndef qualify(old,new,cutoff,done,upper):\n    require(instant(cutoff)<=instant(done)<=instant(upper))\n    return qualify_resume(old,new,"+repr(RUN)+",cutoff,'2026-10-13T18:52:04.958394+00:00',upper)\n"
    raw=constant(raw,'ORACLE',oracle)
    if check(raw,'<current resume whole seal>'):raise ValueError('all current whole seal globals required')
    compile(raw,'<current same-source resume whole seal>','exec');return raw


def main():
    raw=inspect.getsource(previous.prior.previous.previous.main)
    for a,b in [('pg2021-fresh-resume-terminal-receipt-v1',TERM),('pg2023-fresh-resume-rows-oracle-v1','pg2366-current-resume-rows-v1'),('pg2019-fresh-resume-live-binding-complete-v1','pg2362-current-resume-live-binding-v1')]:raw=raw.replace(a,b)
    raw=raw.replace("payload(live['binding'])","payload({**live['binding'],'rootPid':live['rootPid']})")
    ns={**previous.prior.previous.previous.__dict__,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'payload':payload}
    exec(compile(raw,'<actual current whole seal transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
