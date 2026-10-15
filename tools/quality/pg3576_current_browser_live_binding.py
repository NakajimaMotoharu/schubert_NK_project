"""Same completed business run and cutoff; actual new Root identity, old activation rejected."""
import inspect
import pg2990_current_resume_live_binding as template
from pg3564_current_browser_resume_sources import bind,SOURCE,BOM
from pg3574_current_browser_resume_once import SLOT as ONCE

SLOT='pg3576-current-browser-live-binding-v1'


def body():
    raw=bind(template.body())
    old='74729e17-91c0-43e7-b01f-74f9e6461d6a'
    if old not in raw:raise ValueError('old completed activation rejection expected')
    return raw.replace(old,'225691a3-e748-42c4-8972-5ffda5de893d')


def main():
    raw=inspect.getsource(template.main).replace('pg2984-current-fresh-resume-once-v1',ONCE)
    ns={**template.__dict__,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'body':body}
    exec(compile(raw,'<new current same-completed-run actual Root binding>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
