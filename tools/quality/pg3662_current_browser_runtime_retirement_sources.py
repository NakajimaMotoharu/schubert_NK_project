"""Exact used zz3564 entry retirement, preserving current stopped ten-key original and native sidecar."""
import inspect
import json
from pyflakes.api import check
import pg2050_fresh_completed_runtime_retirement_sources as generator
import pg3192_browser_runtime_retirement_sources as template
import pg3600_current_browser_owned_sources as stopped
from pg1446_current_cold_stage import W

SOURCE=stopped.SOURCE
TOOLS='pg3662-current-browser-runtime-retirement-tools-v1'
BASE='/var/lib/pgpt-s1-preservation/pg3600-native-stop-v1/after.private.json'
SHA='e12ce6adc3a4c1641f099a4f01d4c35a7728a6a06c8bd68876e1fcdd7169d38e'
RUNTIME_SHA='7746af83392a9237ff2bf0af650732f0bfc568824c3129c1ee6c6fe4bab632af'


def contract_source():
    proof=json.loads((W/'pg3660-current-runtime-retirement-input-v1/manifest.safe.json').read_bytes())
    if not(proof['actualExit']==0 and proof['productionSource']==SOURCE and proof['guest']['stoppedAfterSha256']==SHA and proof['guest']['targetSha256']==RUNTIME_SHA and proof['guest']['targetBytes']==644):
        raise ValueError('actual full stopped image and current exact runtime entry required')
    raw=template.contract_source()
    for old,new in [('zz-pg3100-once-resume.conf','zz-pg3564-once-resume.conf'),('0dc63b79-3f9a-450c-b2a6-56f86272d272','e1ee096d-370b-4ab9-915a-7c124207e854'),('abe8732db9bad858e6d1b27e541ded5f0d82bf68998c710a757464f4eee9fbbd',RUNTIME_SHA)]:
        if old not in raw:raise ValueError('one diagnosed current literal runtime contract binding required')
        raw=raw.replace(old,new)
    compile(raw,'<exact current used644-byte runtime retirement>','exec');return raw


def sources():
    raw=inspect.getsource(generator.sources)
    for old,new in [('pg2040-fresh-normal-warning-terminal-post-v1','pg3606-current-browser-owned-post-v1'),
                    ('pg2050','pg3662'),('Pg2050','Pg3662'),('PG2050','PG3662'),
                    ('pg2030','pg3600'),('Pg2030','Pg3600'),('PG2030','PG3600'),
                    ("replace('2030','2050')","replace('3600','3662')"),
                    ("replace('1224','2050')","replace('1224','3662')"),
                    ('pg2025-fresh-resume-full-live-seal-v1','pg3650-current-browser-composite-full-seal-v2'),
                    ('8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788','8e1f1899db86f7292a61a0ca0e61f63f13db40371b14221c5d9c332031dd15e1')]:raw=raw.replace(old,new)
    ns={**generator.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'BASE':BASE,'SHA':SHA,'stop_sources':stopped.sources,'contract_source':contract_source}
    exec(compile(raw,'<current full original runtime-only retirement generator>','exec'),ns)
    values=ns['sources']()
    for name,body in values.items():
        body=body.replace('pg3662-current-browser-owned-stop-tools-v1',TOOLS)
        if any(x in body for x in ['pg2050','Pg2050','pg2030','Pg2030','zz-pg3100','PG2802','pg2802']):raise ValueError('legacy final runtime role '+name)
        if name.endswith('.py'):
            if check(body,'<actual current runtime '+name+'>'):raise ValueError('complete final runtime globals required')
            compile(body,'<actual current runtime>','exec')
        values[name]=body
    if len(values)!=17:raise ValueError('complete seventeen source closure required')
    return values
