"""BUG1199: new readonly capture slot with actual generated whole-source static check."""
import inspect
import pg2017_fresh_resume_live_binding as prior

SLOT='pg2019-fresh-resume-live-binding-complete-v1'


def body():
    raw=prior.body();old='import datetime,hashlib,json,os,pathlib,stat,subprocess,time,uuid'
    if raw.count(old)!=1:raise ValueError('one actual unused import boundary required')
    raw=raw.replace(old,'import datetime,hashlib,json,os,pathlib,stat,subprocess,uuid')
    from pyflakes.api import check
    if check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n'+raw,'<actual readonly binding whole source>'):raise ValueError('all binding globals required')
    compile(raw,'<new slot actual readonly source>','exec');return raw


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'body':body}
    exec(compile(inspect.getsource(prior.main),'<new immutable fullsource capture entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
