"""Read-only current new activation, same completed run/cutoff, old activation rejected."""
import inspect
from pyflakes.api import check
import pg3576_current_browser_live_binding as previous
import pg3844_current_resume_sources as role
from pg3854_current_completed_resume_once import SLOT as ONCE

SLOT='pg3856-current-resume-live-binding-v1'


def body():
    raw=role.bind(previous.body())
    for old,new in [(role.previous.RUN,role.RUN),('2026-10-15T16:49:02.160964Z','2026-10-16T00:42:20.585755Z'),('225691a3-e748-42c4-8972-5ffda5de893d','e7584da8-7f80-4f8e-a46c-f46b2388e773')]:
        if old not in raw:raise ValueError('exact current positive live binding missing '+old)
        raw=raw.replace(old,new)
    if check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n'+raw,'<current same run new activation>'):raise ValueError('complete readonly live namespace')
    compile(raw,'<same cutoff new activation actual identity>','exec');return raw


def main():
    values={**previous.template.__dict__,'SLOT':SLOT,'SOURCE':role.SOURCE,'BOM':role.BOM,'body':body}
    # Use the concrete transport rather than a legacy wrapper's own body binding.
    concrete=inspect.getsource(previous.template.main).replace('pg2984-current-fresh-resume-once-v1',ONCE)
    exec(compile(concrete,'<current new activation readonly transport>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
