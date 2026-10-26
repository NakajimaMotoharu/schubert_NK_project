"""Independent declaration/token and static/class-byte post; target Tests never run."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from public_java_digest_provenance import LEX

BASE = '095720ee2766cd9f0bd441ee4bc019833fde8184'
SOURCE = '95894757e2bd7f392262497ea620873430ccc5f1'
OUT = data.BASE/'PG10614-log-cleanup-literal-post-v1'


def original_source(after,constants):
    declarations = []
    replacements = {}
    for row in constants:
        name,value,count = row['name'],row['value'],row['references']
        pattern = r'\bprivate\s+static\s+final\s+String\s+'+re.escape(name)+r'\s*=\s*("(?:\\.|[^"\\])*")\s*;'
        found = list(re.finditer(pattern,after))
        if len(found) != 1 or json.loads(found[0].group(1)) != value:
            raise ValueError('one same-value constant declaration required')
        declarations.append((found[0].start(),found[0].end()))
        replacements[name] = (json.dumps(value),count)
    result = after
    for start,end in sorted(declarations,reverse=True):
        result = result[:start]+result[end:]
    parts, start = [], 0
    actual = Counter()
    for match in LEX.finditer(result):
        if match.group() in replacements:
            name = match.group()
            parts.extend((result[start:match.start()],replacements[name][0]))
            start = match.end()
            actual[name] += 1
    parts.append(result[start:])
    if actual != Counter({k:v[1] for k,v in replacements.items()}):
        raise ValueError('all original literal references required')
    return ''.join(parts)


def finding_identity(row):
    return tuple(sorted((k,v) for k,v in row.items() if k not in ('beginline','endline','begincolumn','endcolumn')))


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    old = data.read_checked(data.BASE/'PG10598-fixed-error-oracle-compile-v1/manifest.json',
        '9f88bf4302849e40fed8a699c391e7552d98af1e2038878d63b4fe4585b44077')
    normal_path = data.BASE/'PG10612-log-cleanup-literal-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    plan = data.read_checked(data.BASE/'PG10608-log-cleanup-literal-plan-v1/manifest.json',
        '806f49d93184aca7d460c885d15d877bdd2531615b2bdcb57a28589e00cec6ab')
    old_static = data.read_checked(data.BASE/'PG10596-fixed-error-oracle-static-v1/manifest.json',
        'e23b29ba95ba12a85c33230b406eb88e25e00216d4671b714374a5ae0c1062f6')
    static = data.read_checked(data.BASE/'PG10610-log-cleanup-literal-static-v1/manifest.json',
        'ece9dc5461f5cd2dd24a1a62c7a4bd3c9d236d8bec737fed23791401f4ceb8b5')
    assert old['source'] == BASE and normal['source'] == SOURCE
    assert old['actualExit'] == normal['actualExit'] == plan['actualExit'] == normal['testsExecuted'] == 0
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(prior)
    changed = {p for p in hashes if hashes[p] != prior[p]}
    assert changed == {r['path'] for r in plan['sourceChanges']} and len(changed) == 2
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    bindings = []
    negatives = 0
    for row in plan['sourceChanges']:
        path = row['path']
        before = subprocess.check_output(['git','show',BASE+':'+path],cwd=data.ROOT).decode()
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == row['beforeSha256'] == prior[path]
        assert row['sha256'] == hashes[path] == static['sourceHashes'][path]
        restored = original_source(after,row['constants'])
        assert canonical(restored) == canonical(before)
        damaged = after.replace('select count(*)','select count(1)',1)
        assert damaged != after
        try:
            damaged_restored = original_source(damaged,row['constants'])
            if canonical(damaged_restored) != canonical(before):
                raise ValueError('SQL alteration detected')
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('altered SQL accepted')
        bindings.append(dict(path=path,beforeSha256=prior[path],sha256=hashes[path]))
    assert negatives == 2
    assert jar_classes(old) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before_test,after_test = test_classes(old),test_classes(normal)
    assert set(before_test) == set(after_test) and len(after_test) == 1962
    byte_changes = sorted(key for key in after_test if after_test[key] != before_test[key])
    assert len(byte_changes) >= 2
    subjects = {(p.split('/')[1].removeprefix('schubert-nk-'),p.split('/src/test/java/')[1].removesuffix('.java')) for p in changed}
    for module,entry in byte_changes:
        stem = entry.removesuffix('.class').split('$')[0]
        assert (module,stem) in subjects
        path = Path(normal['jars'][module]['path']).parent/'test-classes'/entry
        assert decode(path.read_bytes(),entry)['sourceFile'] == stem.rpartition('/')[2]+'.java'
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 39
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    remaining = [r for r in old_static['reports']['pmd']['details'] if r['rule'] != 'AvoidDuplicateLiterals']
    assert len(remaining) == 39 and Counter(map(finding_identity,remaining)) == Counter(map(finding_identity,static['reports']['pmd']['details']))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,baseSource=BASE,invocation=invocation,
        sourceChanges=bindings,compileManifestSha256=data.sha(normal_path.read_bytes()),
        planManifestSha256=data.sha((data.BASE/'PG10608-log-cleanup-literal-plan-v1/manifest.json').read_bytes()),
        staticManifestSha256=data.sha((data.BASE/'PG10610-log-cleanup-literal-static-v1/manifest.json').read_bytes()),
        mainClassesUnchanged=1843,otherTestClassesUnchanged=1962-len(byte_changes),physicalTestClassesChanged=len(byte_changes),
        changedTestClasses=[dict(module=m,entry=p) for m,p in byte_changes],totalTestClasses=1962,
        sameValueConstants=11,references=64,independentMetadataNegativeVectors=negatives,
        duplicateFindingsRemoved=11,remainingFindings=39,remainingNonPositionFindingAttributesUnchanged=True,
        remainingApplicability='PENDING_NOT_WHOLE_F03',productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',
        coverage=None,externalActions=0,oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
