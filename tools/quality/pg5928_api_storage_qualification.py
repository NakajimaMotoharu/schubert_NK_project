"""Read original3973/Jar/all1666 bytes and actual17 targets; never replay PT/runtime."""
import inspect
import re
import subprocess
from pyflakes.api import check
import pg5888_terminal_serial_qualification as previous
from pg5926_api_storage_whole import SOURCE, ROOT, W, SLOT as ORIGINAL, MODIFIED
from pg5906_storage30_static import MODIFIED as STORAGE, class_key
from pg5914_api_expression_static import MODIFIED as API

SLOT = 'pg5928-api-storage-qualified-v1'
PHYSICAL_KINDS = {class_key(p): 'STORAGE_CONSTANT_PRIVATE_LOCK' for p in STORAGE}
PHYSICAL_KINDS.update({class_key(p): 'API_EXPRESSION_ONLY' for p in API})
PHYSICAL_KINDS.update({'storage:dev/codex/schubert/nk/storage/' + n + '.class': 'STORAGE_OWNER_DEBUG_ONLY' for n in ('LinuxSealedProof$Descriptor', 'OwnedTransferDirectory$EntryHandle', 'StorageRootInspection$Inode')})
PHYSICAL_KINDS.update({'api:dev/codex/schubert/nk/api/application/admin/UserCommandService$' + n + '.class': 'API_OWNER_DEBUG_ONLY' for n in ('Change', 'State', 'Update', 'Values')})


def physical_difference(old, new, candidate):
    if len(old) != 1666 or len(new) != 1666 or new != candidate or set(old) != set(new) or {k for k in old if old[k] != new[k]} != set(PHYSICAL_KINDS) or len(PHYSICAL_KINDS) != 16:
        raise ValueError('all1666 actual bytes; exact16 modified/1650 unchanged, no added/removed')
    if any(re.fullmatch('[0-9a-f]{64}', value) is None for mapping in (old, new, candidate) for value in mapping.values()):
        raise ValueError('actual SHA256 only')
    return [dict(oldClass=k, **{'class': k}, oldSha256=old[k], newSha256=new[k], action='MODIFIED', physicalKind=PHYSICAL_KINDS[k]) for k in sorted(PHYSICAL_KINDS)], 1650


def added_cases():
    paths = subprocess.check_output(['git', 'diff', '--name-only', previous.SOURCE, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(paths) != MODIFIED or any('/src/test/' in p for p in paths):
        raise ValueError('nine declared Main changes only; all3973 original Test identities unchanged')
    return []


def qualifier_source():
    raw = previous.qualifier_source()
    changes = {
        "out = base / 'runs/PG5886-six-v1'": "out = base / 'runs/PG5926-six-v1'",
        "source = base / 'source-full-PG5886'": "source = base / 'source-full-PG5926'",
        "old = base / 'runs/PG5860-six-v1'": "old = base / 'runs/PG5886-six-v1'",
        'transfer/PG5886-source.tar': 'transfer/PG5926-source.tar',
        'len(oldcases) == 3971': 'len(oldcases) == 3973', 'len(additions) == 2': 'len(additions) == 0',
        'all3971 original identities retained plus exact2 legal Sync concurrency contracts; no oracle change': 'all3973 original identities retained; no Test/oracle/resource changes after storage/API PG'}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one current original3973 qualification binding: ' + old)
        raw = raw.replace(old, new, 1)
    return raw


def current_changed_counters(value):
    import hashlib
    import pathlib
    import xml.etree.ElementTree as ET
    targets = {'storage': ('LinuxExecDescriptors', 'LinuxFilesystemClassifier', 'LinuxSealedProof', 'StorageAttributeGuard', 'StorageRootInspection', 'OwnedTransferDirectory'),
               'api': ('application/admin/UserCommandService', 'file/AssetChecksumManifest', 'idempotency/WipingByteArrayOutputStream')}
    result = {}
    for module, names in targets.items():
        path = pathlib.Path('/home/mini/schubert-nk-pgpt/source-full-PG5926/src/schubert-nk-' + module + '/target/site/jacoco/jacoco.xml')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != value['modules'][module]['coverageXmlSha256']:
            raise ValueError('actual original whole coverage hash unchanged')
        classes = {c.get('name'): c for c in ET.fromstring(raw).findall('package/class')}
        for name in names:
            full = 'dev/codex/schubert/nk/' + module + '/' + name
            result[module + ':' + full] = {c.get('type'): {'covered': int(c.get('covered')), 'missed': int(c.get('missed'))} for c in classes[full].findall('counter') if c.get('type') in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
    if len(result) != 9 or any(set(c) != {'LINE', 'METHOD', 'CLASS', 'BRANCH'} for c in result.values()):
        raise ValueError('all nine actual changed executable targets')
    return result


def emitted(data):
    raw = previous.emitted(data)
    physical, qualifier = inspect.getsource(previous.physical_difference), previous.qualifier_source()
    prefix = 'PHYSICAL_KINDS=' + repr(previous.PHYSICAL_KINDS)
    if raw.count(physical) != 1 or raw.count(qualifier) != 1 or raw.count(prefix) != 1:
        raise ValueError('one complete physical and original XML reader definition')
    raw = raw.replace(physical, inspect.getsource(physical_difference), 1).replace(qualifier, qualifier_source(), 1).replace(prefix, 'PHYSICAL_KINDS=' + repr(PHYSICAL_KINDS), 1).replace('source-full-PG5886', 'source-full-PG5926')
    ending = 'print(__import__("json").dumps(value))\n'
    if raw.count(ending) != 1:
        raise ValueError('one final qualified artifact result')
    raw = raw.replace(ending, '', 1)
    raw += inspect.getsource(current_changed_counters) + '\nvalue["currentChangedTargetCounters"]=current_changed_counters(value)\n'
    raw += 'value["currentChangedNineTargetFour100"]=all(c[k]["missed"]==0 and(c[k]["covered"]>0 or k=="BRANCH")for c in value["currentChangedTargetCounters"].values()for k in("LINE","METHOD","CLASS","BRANCH"))\n'
    raw += 'value["allSeventeenTargetFour100"]=value["currentChangedNineTargetFour100"] and value["coreReceiverTargetFour100"]\n' + ending
    if check(raw, '<current3973 independent original reader>'):
        raise ValueError('complete generated namespace')
    compile(raw, '<current3973 independent reader>', 'exec')
    return raw


def operator_source():
    raw = previous.operator_source()
    changes = {'PG5886-six-v1': 'PG5926-six-v1', 'PG5860-current3971-cases': 'PG5886-current3973-cases',
               'a937e6dc41450d13b2874299d28f19caafc5b0b070fffdd4c96669bc410c3d02': '2045f1a9eb4eb60f2f470442bfbd3774f2925ce17cc88b5875d16f1163778d7f',
               'PG5882-terminal-serial-static-v1': 'PG5914-api-expression-static-v1',
               'pg5882-terminal-serial-static-v1': 'pg5914-api-expression-static-v1', 'PG5888-qualified-v1': 'PG5928-qualified-v1'}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one original3973 operator binding: ' + old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<current3973 independent operator>', 'exec')
    return raw


def main():
    scope = {**vars(previous.previous.previous), 'SOURCE': SOURCE, 'ROOT': ROOT, 'W': W, 'ORIGINAL': ORIGINAL,
             'SLOT': SLOT, 'PHYSICAL_KINDS': PHYSICAL_KINDS, 'physical_difference': physical_difference, 'added_cases': added_cases, 'emitted': emitted}
    exec(compile(operator_source(), '<current3973 independent operator>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
