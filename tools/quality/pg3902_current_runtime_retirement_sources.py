"""Exact current one-file retirement graph with whole-generation immutable capsule protection."""
import inspect
import json
from pyflakes.api import check
import pg2050_fresh_completed_runtime_retirement_sources as generator
import pg3876_current_resume_owned_sources as stopped
from immutable_payload_binding import transform_bundle_preserving_payloads
from pg3900_current_runtime_retirement_input import SOURCE,BASE,SHA
from pg1446_current_cold_stage import W

TOOLS='pg3902-current-resume-runtime-retirement-tools-v1'
RUNTIME_SHA='bfa7d75b74fccd6a29e319739fded4eabd74647e24e426a7fabb4e108be91cba'


def contract_source():
    proof=json.loads((W/'pg3900-current-runtime-retirement-input-v1/manifest.safe.json').read_bytes())
    if not(proof['actualExit']==0 and proof['productionSource']==SOURCE and proof['guest']['stoppedAfterSha256']==SHA and proof['guest']['targetSha256']==RUNTIME_SHA and proof['guest']['targetBytes']==644):
        raise ValueError('actual exact current644/runtime input required')
    raw=inspect.getsource(generator.contract)
    for old,new in [('zz-pg1160-once-resume.conf','zz-pg3844-once-resume.conf'),('343a5a1b-d064-47d5-88c2-31c36d7ba7a4','f29290f8-69ed-49fe-9f2f-33b4efdea422'),('d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0',RUNTIME_SHA),('1,647','1,644'),('os.read(fd,648)','os.read(fd,645)'),('len(data)==647','len(data)==644')]:
        if old not in raw:raise ValueError('exact independent retirement contract role required '+old)
        raw=raw.replace(old,new)
    compile(raw,'<exact current644 held FD runtime retirement>','exec');return raw


def transform(seed):
    raw=inspect.getsource(generator.sources)
    for old,new in [('pg2040-fresh-normal-warning-terminal-post-v1','pg3882-current-resume-owned-post-v1'),
                    ('pg2050','pg3902'),('Pg2050','Pg3902'),('PG2050','PG3902'),
                    ('pg2030','pg3876'),('Pg2030','Pg3876'),('PG2030','PG3876'),
                    ("replace('2030','2050')","replace('3876','3902')"),
                    ("replace('1224','2050')","replace('1224','3902')"),
                    ('pg2025-fresh-resume-full-live-seal-v1','pg3870-current-resume-composite-full-seal-v1'),
                    ('8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788','c9912bbe731d3a30650daeb84138da5d987a69984fa9b6aef332630bab822405')]:raw=raw.replace(old,new)
    # Protect for the complete inherited generator, including its initial seed
    # and every later rewrite/compile check. Restore before final name analysis.
    marker="    for name,body in values.items():"
    if raw.count(marker)!=1:raise ValueError('single final restored namespace-check boundary')
    # This transformation is called with already masked source capsules. The
    # inherited generator only compiles them; it never executes the capsules.
    raw=raw[:raw.index(marker)]+"    return values\n"
    values={**generator.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'BASE':BASE,'SHA':SHA,
        'stop_sources':lambda:seed,'contract_source':contract_source}
    exec(compile(raw,'<current entire retirement generation>','exec'),values)
    return {name:body.replace('pg3902-current-resume-owned-tools-v1',TOOLS)for name,body in values['sources']().items()}


def sources():
    values=transform_bundle_preserving_payloads(stopped.sources(),transform)
    if len(values)!=17:raise ValueError('exact seventeen-file complete retirement graph required')
    for name,raw in values.items():
        if name.endswith('.py'):
            if check(raw,'<complete current restored retirement '+name+'>'):raise ValueError('all restored Python globals required')
            compile(raw,'<restored current retirement source>','exec')
        values[name]=raw
    return values
