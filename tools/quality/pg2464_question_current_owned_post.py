"""Independent whole new current stopped post, never reissue the stop."""
import inspect
import json
from pyflakes.api import check
import pg2380_current_resume_owned_post as prior
from pg2458_question_current_owned_sources import context,TOOLS,SOURCE,BOM
from pg1446_current_cold_stage import W

SLOT='pg2464-question-current-owned-post-v1'


def emit(seals,ctx,live):
    raw=prior.emit(seals,ctx,live)
    for a,b in [(prior.TOOLS,TOOLS),('pg2374','pg2458'),('Pg2374','Pg2458'),('PG2374','PG2458'),
                (prior.SLOT,SLOT),('PG2380-current-resume-owned-post-v1','PG2464-question-current-owned-post-v1'),
                ('pg2368-current-resume-full-seal-v1','pg2456-question-current-full-seal-v1'),
                (prior.SOURCE,SOURCE),(prior.BOM,BOM),('PG2126','PG2428'),('pg2126-manifest.sig','pg2428-manifest.sig')]:raw=raw.replace(a,b)
    if check('HASHES={}\nRECEIPT="actual"\n'+raw,'<current new stopped whole post>'):raise ValueError('actual current stopped namespace required')
    compile(raw,'<whole current new source stopped post>','exec');return raw


def payload(seals):
    live=json.loads((W/'pg2450-question-current-live-binding-v1/manifest.safe.json').read_bytes())
    return emit(seals,context(),live)


def entry():
    raw=inspect.getsource(prior.previous.prior.prior.prior.previous.main)
    for a,b in [('pg2038-stop-v1','pg2460-stop-v1'),('pg2031-frozen-v1','pg2459-frozen-v1'),
                ('pg2030_parent_receipt.py','pg2458_parent_receipt.py'),('pg2030-native-stop-v1','pg2458-native-stop-v1')]:raw=raw.replace(a,b)
    ns={**prior.previous.prior.prior.prior.previous.__dict__,'SLOT':SLOT,'TOOLS':TOOLS,'SOURCE':SOURCE,'BOM':BOM,'payload':payload}
    exec(compile(raw,'<new current independent stopped post entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
