"""One new signed candidate and authenticated retired current role graph, source factory only."""
import json
import re
from pyflakes.api import check
import pg2144_normal_unused_fixed_sources as prior
import pg2132_current_normal_unused_sources as old_roles
import pg2374_current_resume_owned_sources as current_parent
from pg2404_question_jdbc_full_six import production
from pg1446_current_cold_stage import W

CURRENT = current_parent.SOURCE
CURRENT_BOM = current_parent.BOM
BEFORE = '9a332efc26ac5d46fff204ef88813668e0501ac7651737b8573c50859fcfc054'
TOOLS = 'pg2412-question-unused-tools-v1'
SAVE = 'pg2416-question-unused-placement-v1'
ARCHIVE = 'pg2414-question-release-v1.tar'
REMOTE = '/home/ubuntu/pg2414-question-input-v1'


def bind(raw):
    # Protect candidate and current roles before replacing overlapping values.
    raw = raw.replace(old_roles.production(), '__NEW_QUESTION_SOURCE__').replace(
        old_roles.CURRENT, CURRENT).replace('__NEW_QUESTION_SOURCE__', production())
    raw = raw.replace('PG2126','__NEW_QUESTION_RELEASE__').replace('pg2126','__NEW_QUESTION_RELEASE_LOWER__').replace(
        'PG1846','PG2126').replace('pg1846','pg2126').replace('__NEW_QUESTION_RELEASE__','PG2428').replace(
        '__NEW_QUESTION_RELEASE_LOWER__','pg2428')
    pairs = [(old_roles.CURRENT_BOM,CURRENT_BOM),(old_roles.BEFORE,BEFORE),
        ('pg2130-current-normal-before-v1','pg2410-retired-current-before-v1'),
        ('a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','91f5484b-9702-4c7c-97f3-dd5110a853f9'),
        ('9026b2ab-bb42-49cd-a2bd-4c661049dce3','e1429ac8-f3dd-4e8c-83d2-1926c4ba8440'),
        ('2026-10-13T03:08:18.452473Z','2026-10-13T15:01:53.237266Z'),
        ('2026-10-13T03:35:44.330028Z','2026-10-13T19:18:53.785844Z'),
        ('2c37fef2a2ff48e7b6a05cfc23f84c19','4011498eef014f25986f4e5ac5c92b1d'),
        (prior.TOOLS,TOOLS),(prior.SAVE,SAVE),(prior.ARCHIVE,ARCHIVE),(prior.REMOTE,REMOTE),
        ('pg2144','pg2412'),('Pg2144','Pg2412'),('PG2144','PG2412'),
        ('pg2132','pg2412'),('Pg2132','Pg2412'),('PG2132','PG2412'),
        ('pg2148','pg2416'),('PG2148','PG2416'),('pg2146','pg2414'),('PG2146','PG2414')]
    for a,b in pairs:
        raw = raw.replace(a,b)
    for a,b in [('113070840714','20469616839'),('114755353173','22107644017'),('588342','104841')]:
        raw = re.sub(r'\b'+a+r'\b',b,raw)
    return raw


def sources(bom, before=BEFORE):
    if before != BEFORE:
        raise ValueError('one actual retired current before required')
    proof = json.loads((W/'pg2410-retired-current-before-v1/manifest.safe.json').read_bytes())
    if proof['actualExit'] != 0 or proof['productionSource'] != CURRENT or proof['privateBeforeSha256'] != BEFORE or not proof['runtimeAlreadyRetired']:
        raise ValueError('actual independent current retired proof required')
    owners = current_parent.sources()
    result = {}
    for name,raw in prior.sources(bom).items():
        name = bind(name)
        if name == 'pg2412_parent_receipt.py':
            raw = owners['pg2374_parent_receipt.py']
        elif name == 'pg2412_warning_parent_projection.py':
            raw = owners['pg2374_warning_parent_projection.py']
        else:
            raw = bind(raw)
        if name.endswith('.py'):
            prelude = "BUNDLE_HASH='pending-real-bundle'\n" if name in {'pg2412_native_refs.py','pg2412_input_preflight.py'} else ''
            if check(prelude+raw,'<new question current graph '+name+'>'):
                raise ValueError('whole declared graph namespace required')
            compile(raw,'<question graph>','exec')
        result[name] = raw
    if any('__NEW_QUESTION' in s for s in result.values()):
        raise ValueError('unbound current/candidate role')
    return result


if __name__ == '__main__':
    raise SystemExit('source factory only; no VM operation')
