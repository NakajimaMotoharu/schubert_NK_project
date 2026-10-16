"""Independent literal retirement-only delta, full11/native46 and all-resource post."""
import inspect
import pg2398_current_runtime_retirement_post as template
import pg3882_current_resume_owned_post as stopped
from immutable_payload_binding import PROTECTED
from pg3902_current_runtime_retirement_sources import contract_source,SOURCE,TOOLS,SHA,BASE

SLOT='pg3908-current-runtime-retirement-post-v1'


def namespace():
    values={**template.__dict__,'previous':stopped,'contract_source':contract_source,'SOURCE':SOURCE,'TOOLS':TOOLS,'SHA':SHA,'BASE':BASE,'SLOT':SLOT,'PROTECTED':PROTECTED}
    for fn in [template.payload,template.main]:
        raw=inspect.getsource(fn)
        for old,new in [('pg2374','pg3876'),('Pg2374','Pg3876'),('pg2392','pg3902'),('Pg2392','Pg3902'),
                        ('PG2380-current-resume-owned-post-v1','PG3882-current-resume-owned-post-v1'),
                        ('PG2398-current-runtime-retirement-post-v1','PG3908-current-runtime-retirement-post-v1'),
                        ('pg2394','pg3906'),('pg2393','pg3904')]:raw=raw.replace(old,new)
        if fn is template.payload:
            marker='    raw=previous.payload(seals).replace'
            if raw.count(marker)!=1:raise ValueError('one code-only post translation boundary required')
            raw=raw.replace(marker,"    original=previous.payload(seals)\n    if any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in n.targets)for n in ast.walk(ast.parse(original))):raise ValueError('embedded immutable data requires whole-bundle protection')\n    raw=original.replace",1)
        exec(compile(raw,'<independent current runtime-only full11 post>','exec'),values)
    return values


def payload(seals):return namespace()['payload'](seals)


def main():return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
