"""Separate exact runtime/config delta, actual all11 incl native34 and zero resources."""
import inspect
import pg2398_current_runtime_retirement_post as template
import pg3606_current_browser_owned_post as stopped
from pg3662_current_browser_runtime_retirement_sources import contract_source,SOURCE,TOOLS,SHA,BASE

SLOT='pg3668-current-browser-runtime-retirement-post-v1'


def namespace():
    ns={**template.__dict__,'previous':stopped,'contract_source':contract_source,'SOURCE':SOURCE,'TOOLS':TOOLS,'SHA':SHA,'BASE':BASE,'SLOT':SLOT}
    for fn in [template.payload,template.main]:
        raw=inspect.getsource(fn)
        for old,new in [('pg2374','pg3600'),('Pg2374','Pg3600'),('pg2392','pg3662'),('Pg2392','Pg3662'),
                        ('PG2380-current-resume-owned-post-v1','PG3606-current-browser-owned-post-v1'),
                        ('PG2398-current-runtime-retirement-post-v1','PG3668-current-browser-runtime-retirement-post-v1'),
                        ('pg2394','pg3666'),('pg2393','pg3664')]:raw=raw.replace(old,new)
        exec(compile(raw,'<independent current runtime-only all11 post>','exec'),ns)
    return ns


def payload(seals):return namespace()['payload'](seals)


def main():return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
