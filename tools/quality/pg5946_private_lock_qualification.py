"""Original5944 qualification/actual34 counter reader; no replay of PT or operations."""
import inspect
import json
import re
import subprocess
from pyflakes.api import check
import pg5928_api_storage_qualification as previous
from pg5944_private_lock_whole import SOURCE, ROOT, W, SLOT as ORIGINAL
from pg5940_private_lock_compile import BASE, OLD, plan, sha

SLOT = 'pg5946-private-lock-qualified-v1'
STATIC = BASE/'PG5942-private-lock-static-v1/manifest.json'
STATIC_SHA = 'fba315bab4168d6150638c7a21b5209dfce88b0f97951e456ed3d52d33edbda5'
PHYSICAL_KINDS = {}  # Bound from the strict current static proof before any qualification.


def physical_kinds():
    if sha(STATIC) != STATIC_SHA:
        raise ValueError('actual independent all1666/54 declared differences')
    value = json.loads(STATIC.read_bytes()); required = set(plan()['requiredClassKeys'])
    return {k: 'PRIVATE_EXCLUSIVE_LOCK_BODY_WRAPPER' if k in required else 'OWNER_DEBUG_ONLY_PROVED_PG5943' for k in value['changedPhysicalClasses']}


def physical_difference(old, new, candidate):
    if len(old) != 1666 or len(new) != 1666 or new != candidate or set(old) != set(new) or {k for k in old if old[k] != new[k]} != set(PHYSICAL_KINDS) or len(PHYSICAL_KINDS) != 54:
        raise ValueError('all1666/54modified/1612identical; actual compile/static/class maps agree')
    if any(re.fullmatch('[0-9a-f]{64}', v) is None for m in (old, new, candidate) for v in m.values()):
        raise ValueError('actual SHA256 maps only')
    return [dict(oldClass=k, **{'class': k}, oldSha256=old[k], newSha256=new[k], action='MODIFIED', physicalKind=PHYSICAL_KINDS[k]) for k in sorted(PHYSICAL_KINDS)], 1612


def added_cases():
    paths = subprocess.check_output(['git', 'diff', '--name-only', OLD, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(paths) != {r['path'] for r in plan()['sourcePlans']}:
        raise ValueError('only33 declared Main; original3973 Test/oracles unchanged')
    return []


def qualifier_source():
    raw = previous.qualifier_source()
    for old, new in (("out = base / 'runs/PG5926-six-v1'", "out = base / 'runs/PG5944-six-v1'"),
                     ("source = base / 'source-full-PG5926'", "source = base / 'source-full-PG5944'"),
                     ("old = base / 'runs/PG5886-six-v1'", "old = base / 'runs/PG5926-six-v1'"),
                     ('transfer/PG5926-source.tar', 'transfer/PG5944-source.tar')):
        if raw.count(old) != 1:
            raise ValueError('exact original/prior archive and run bindings')
        raw = raw.replace(old, new, 1)
    return raw


def private_lock_counters(data, value):
    import hashlib
    import pathlib
    import xml.etree.ElementTree as ET
    targets = data['privateLockTargets']; result = {}; xmls = {}
    for key in targets:
        module, name = key.split(':', 1); name = name[:-6]
        if module not in xmls:
            p = pathlib.Path('/home/mini/schubert-nk-pgpt/source-full-PG5944/src/schubert-nk-'+module+'/target/site/jacoco/jacoco.xml')
            raw = p.read_bytes()
            if hashlib.sha256(raw).hexdigest() != value['modules'][module]['coverageXmlSha256']:
                raise ValueError('actual original5944 XML hash fixed')
            xmls[module] = {c.get('name'): c for c in ET.fromstring(raw).findall('package/class')}
        if name not in xmls[module]:
            raise ValueError('actual target class coverage cannot be absent')
        result[key] = {c.get('type'): {'covered': int(c.get('covered')), 'missed': int(c.get('missed'))} for c in xmls[module][name].findall('counter') if c.get('type') in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
    if len(result) != 34 or any(set(v) != {'LINE', 'METHOD', 'CLASS', 'BRANCH'} for v in result.values()):
        raise ValueError('all34 actual target counters explicit; no inferred measures')
    return result


def emitted(data):
    raw = previous.emitted(data)
    replacements = ((inspect.getsource(previous.physical_difference), inspect.getsource(physical_difference)),
                    (previous.qualifier_source(), qualifier_source()),
                    ('PHYSICAL_KINDS='+repr(previous.PHYSICAL_KINDS), 'PHYSICAL_KINDS='+repr(physical_kinds())))
    for old, new in replacements:
        if raw.count(old) != 1:
            raise ValueError('complete one physical/qualifier definition replacement')
        raw = raw.replace(old, new, 1)
    raw = raw.replace('source-full-PG5926', 'source-full-PG5944')
    end = 'print(__import__("json").dumps(value))\n'
    if raw.count(end) != 1:
        raise ValueError('one qualified result emission')
    raw = raw.replace(end, '', 1)+inspect.getsource(private_lock_counters)+'\nvalue["privateLockTargetCounters"]=private_lock_counters(data,value)\n'
    raw += 'value["privateLock34TargetFour100"]=all(c[k]["missed"]==0 and c[k]["covered"]>0 for c in value["privateLockTargetCounters"].values() for k in("LINE","METHOD","CLASS","BRANCH"))\n'+end
    if check(raw, '<independent private-lock original3973 reader>'):
        raise ValueError('complete generated reader namespace')
    compile(raw, '<actual5944 independent reader>', 'exec')
    return raw


def operator_source():
    raw = previous.operator_source()
    for old, new in (('PG5926-six-v1', 'PG5944-six-v1'), ('PG5886-current3973-cases', 'PG5926-current3973-cases'),
                     ('2045f1a9eb4eb60f2f470442bfbd3774f2925ce17cc88b5875d16f1163778d7f', '89bdeed7bf69067bb0a20c766c8e59cbb780d0fd83dffa7e71c9e1255b1115cf'),
                     ('PG5914-api-expression-static-v1', 'PG5942-private-lock-static-v1'), ('pg5914-api-expression-static-v1', 'pg5942-private-lock-static-v1'),
                     ('PG5928-qualified-v1', 'PG5946-qualified-v1')):
        if raw.count(old) != 1:
            raise ValueError('exact current5944 original operator binding')
        raw = raw.replace(old, new, 1)
    before = '    raw=emitted(data);'
    if raw.count(before) != 1:
        raise ValueError('one target declaration before reader emission')
    raw = raw.replace(before, '    data["privateLockTargets"]='+repr(plan()['requiredClassKeys'])+'\n'+before, 1)
    compile(raw, '<original5944 reader operator>', 'exec')
    return raw


def main():
    global PHYSICAL_KINDS
    kinds = physical_kinds()
    PHYSICAL_KINDS = kinds
    scope = {**vars(previous.previous.previous.previous), 'SOURCE': SOURCE, 'ROOT': ROOT, 'W': W, 'ORIGINAL': ORIGINAL,
             'SLOT': SLOT, 'BASE': BASE, 'PHYSICAL_KINDS': kinds, 'physical_difference': physical_difference,
             'added_cases': added_cases, 'emitted': emitted}
    exec(compile(operator_source(), '<original5944 operator>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
