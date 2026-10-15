"""New-only completed-run resume graph from pinned successful bytes, not old authority."""
import ast
import hashlib
import json
import re
from pyflakes.api import check
from pg1446_current_cold_stage import W

SOURCE='4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
BOM='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72'
BOOT='79a3260a-e16d-42bf-942a-b914ed144c28'
RUN='e1ee096d-370b-4ab9-915a-7c124207e854'
BEFORE='27c42f2bc1e455615ddaaec706668ebcdb10179fe082d203dba8e129be10a049'
BASELINE='/var/lib/pgpt-s1-preservation/pg3560-current-full11-baseline-v1/before.private.json'
TOOLS='pg3564-current-browser-resume-tools-v1'
SAVE='pg3568-current-browser-resume-preparation-v1'
CLASS='Pg3564FreshResumePreparation'
OLD=W/'pg3100-full-native-resume-tools-v1'
CURRENT=W/'pg3520-outbox-owned-stop-tools-v2'


def pinned(root,name):
    pins=json.loads((root/'payload-sha256.json').read_bytes())
    raw=(root/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pins[name]:
        raise ValueError('frozen successful input byte mismatch')
    return raw.decode()


def bind(raw):
    for old,new in [
        ('pg3100-full-native-resume-tools-v1',TOOLS),
        ('pg3104-full-native-resume-preparation-v1',SAVE),
        ('pg3100','pg3564'),('Pg3100','Pg3564'),('PG3100','PG3564'),
        ('pg3102','pg3566'),('pg3104','pg3568'),('pg3106','pg3570'),
        ('PG3106','PG3570'),
        ('/var/lib/pgpt-s1-preservation/pg3034-native-stop-v1/after.private.json',BASELINE),
        ('92c953ea49001ec6cca15073665e6c4ae939485c08f66a91bf3f597ddc0d7ece',BEFORE),
        ('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',SOURCE),
        ('37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863',BOM),
        ('PG2802','PG3420'),('pg2802','pg3420'),
        ('0dc63b79-3f9a-450c-b2a6-56f86272d272',RUN),
        ('0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf','225691a3-e748-42c4-8972-5ffda5de893d'),
        ('2026-10-14T19:12:28.842213Z','2026-10-15T16:49:02.160964Z'),
        ('2026-10-14T23:27:40.948070Z','2026-10-15T17:16:54.836275Z'),
        ('65ad6798d497474685fa32d6750cea1f','01dd090d1eef4b2ea13afa18cfc00155'),
    ]:
        raw=raw.replace(old,new)
    # Exact numeric tokens only: never alter an embedded SHA substring.
    for old,new in [('18100986959','82190409233'),('19749542200','83898942386'),('122976','321930')]:
        raw=re.sub(r'(?<![A-Za-z0-9])'+old+r'(?![A-Za-z0-9])',new,raw)
    return raw


def sources():
    proof=json.loads((W/'pg3560-current-full11-baseline-v1/manifest.safe.json').read_bytes())
    if not (proof['actualExit']==0 and proof['productionSource']==SOURCE
            and proof['guest']['snapshotKeys']==11 and proof['guest']['privateBeforeSha256']==BEFORE
            and proof['guest']['newTenRefsReturnedNormally'] and proof['guest']['runtimeOnlyOriginalEmptyParent']):
        raise ValueError('fresh independently read complete stopped baseline required')
    values={bind(p.name):bind(pinned(OLD,p.name)) for p in OLD.iterdir() if p.suffix in {'.py','.java'}}
    if len(values)!=20: raise ValueError('exact successful twenty source roles required')
    # Current positive/negative receipt tuples already have independently tested
    # authorities. Rename their namespace only; never rewrite their negative UUIDs.
    for suffix in ['parent_receipt','warning_parent_projection','configuration','configuration_capture','row_bound','stable_journal']:
        values['pg3564_'+suffix+'.py']=pinned(CURRENT,'pg3520_'+suffix+'.py').replace('pg3520','pg3564').replace('PG3520','PG3564')
    original=pinned(CURRENT,'Pg3520OriginalTupleTest.java').replace('Pg3520NativeStop',CLASS).replace('Pg3520','Pg3564').replace('PG3520','PG3564')
    values['Pg3564OriginalTupleTest.java']=original
    current=pinned(CURRENT,'Pg3520NativeStop.java')
    start=current.index('  static void verifyOriginalValues(')
    method=current[start:current.index('\n  static void verifyOriginal()',start)]
    raw=values[CLASS+'.java'];start=raw.index('  static void verifyOriginalValues(')
    end=raw.index('\n  static void verifyOriginal()',start)
    values[CLASS+'.java']=raw[:start]+method+raw[end:]
    for name,raw in values.items():
        if any(s in raw for s in ['pg3100','Pg3100','PG3100','pg3034','PG2802','pg2802','a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25']):
            raise ValueError('old positive role in emitted '+name)
        if name.endswith('.py'):
            if check(raw,'<current Browser final '+name+'>'): raise ValueError('complete generated globals required')
            compile(raw,'<current Browser final '+name+'>','exec')
    refs=values['pg3564_native_refs.py']
    capture=next(n for n in ast.walk(ast.parse(refs)) if isinstance(n,ast.FunctionDef) and n.name=='capture_data')
    returns=[n.value for n in ast.walk(capture) if isinstance(n,ast.Return) and isinstance(n.value,ast.Dict)]
    if len(returns)!=1 or len(returns[0].keys)!=11 or 'native' not in [k.value for k in returns[0].keys]:
        raise ValueError('all eleven actual fields including native required')
    if 'require(set(prior) == set(first) and same_value(first, prior))' not in refs:
        raise ValueError('strict complete original equality required')
    return values
