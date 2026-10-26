"""Independent same-value source/byte/static-context binding; no Product Test execution."""
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

BASE = '95894757e2bd7f392262497ea620873430ccc5f1'
SOURCE = '370fd74f6f170a18bc1bf959aa9fceced0def15a'
OUT = data.BASE/'PG10634-query-semantic-constant-post-v1'


def original_source(text,path):
    values = {'FIXTURE_FIRST_COMMIT_ORDINAL':('1',3),
              'FIXTURE_SECOND_COMMIT_ORDINAL':('2',1),
              'FIXTURE_THIRD_COMMIT_ORDINAL':('3',1)}
    if path.endswith('/LogQueryApplicationServiceTest.java'):
        for name,(value,count) in values.items():
            pattern = r'\bprivate\s+static\s+final\s+int\s+'+name+r'\s*=\s*'+value+r'\s*;'
            if len(re.findall(pattern,text)) != 1:
                raise ValueError('one fixed ordinal declaration required')
            text = re.sub(pattern,'',text,count=1)
            if len(re.findall(r'\b'+name+r'\b',text)) != count:
                raise ValueError('five ordinal references preserved')
        return ' '.join(values[m.group()][0] if m.group() in values else m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*')))
    if path.endswith('/UserQueryApplicationServiceTest.java'):
        if 'SYSTEM_ERROR_RESULT' in text or len(re.findall(r'\bIDEMPOTENT_RESULT\b',text)) != 8:
            raise ValueError('all eight declaration/reference identifiers renamed')
        if not re.search(r'\bString\s+IDEMPOTENT_RESULT\s*=\s*"0200"\s*;',text):
            raise ValueError('UI232 idempotent success literal unchanged')
        return ' '.join('SYSTEM_ERROR_RESULT' if m.group() == 'IDEMPOTENT_RESULT' else m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*')))
    raise ValueError('only two declared source paths')


def finding_identity(row):
    return {k:v for k,v in row.items() if k not in ('beginline','endline','begincolumn','endcolumn')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    old = data.read_checked(data.BASE/'PG10612-log-cleanup-literal-compile-v1/manifest.json',
        '7e484e3e66d5f8b678c933a8628d40e4ecb7d145d1f426d8372c9e22d411fcf1')
    normal_path = data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    plan = data.read_checked(data.BASE/'PG10628-query-semantic-constant-plan-v1/manifest.json',
        'e8a26780228c4ac1f7cb9e845ad1795087a66730a5cd61ac04fc9edf6b0cdeb0')
    static = data.read_checked(data.BASE/'PG10630-query-semantic-constant-static-v1/manifest.json',
        '1c3a44d5d4cd9f42b5370c070565fd1a7438821bad75c1b57aac368b7fa0003c')
    review_path = data.BASE/'PG10622-query-test-static-context-v1/manifest.json'
    review = data.read_checked(review_path,'606712ec61dc8240a3a46c13002001a0badd213255b427a681300e1c6c944db9')
    independent = data.read_checked(data.BASE/'PG10624-query-test-static-context-post-v1/manifest.json',
        '52f29ad6d21fe887322b87140f7a3dcc1fa3d80712eacbeb34dd411ba7d5c4ba')
    assert review['source'] == independent['source'] == old['source'] == BASE
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == plan['actualExit'] == independent['actualExit'] == 0
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(prior)
    changed = {p for p in hashes if hashes[p] != prior[p]}
    assert changed == {r['path'] for r in plan['sourceChanges']} and len(changed) == 2
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    bindings, negatives = [], 0
    for row in plan['sourceChanges']:
        path = row['path']
        before = subprocess.check_output(['git','show',BASE+':'+path],cwd=data.ROOT).decode()
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == row['beforeSha256'] == prior[path]
        assert row['sha256'] == hashes[path] == static['sourceHashes'][path]
        assert canonical(original_source(after,path)) == canonical(before)
        sample = after.replace('assertEquals(0,','assertEquals(999,',1)
        assert sample != after
        assert canonical(original_source(sample,path)) != canonical(before)
        negatives += 1
        bindings.append(dict(path=path,beforeSha256=prior[path],sha256=hashes[path]))
    old_main,new_main = jar_classes(old),jar_classes(normal)
    assert old_main == new_main and len(new_main) == 1843
    old_test,new_test = test_classes(old),test_classes(normal)
    assert set(old_test) == set(new_test) and len(new_test) == 1962
    byte_changes = sorted(k for k in new_test if old_test[k] != new_test[k])
    subjects = {(p.split('/')[1].removeprefix('schubert-nk-'),p.split('/src/test/java/')[1].removesuffix('.java')) for p in changed}
    assert len(byte_changes) >= 2
    for module,entry in byte_changes:
        stem = entry.removesuffix('.class').split('$')[0]
        assert (module,stem) in subjects
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/entry
        assert decode(file.read_bytes(),entry)['sourceFile'] == stem.rpartition('/')[2]+'.java'
    judgments = data.read_checked(review_path.parent/'judgments.json',review['judgmentsSha256'])
    remaining = [r for r in judgments if r['disposition'] == 'NOT_APPLICABLE_TO_EXACT_TEST_CONTEXT']
    current = static['reports']['pmd']['details']
    assert len(remaining) == len(current) == 34
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 34
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    rebinding = []
    for original,finding in zip(remaining,current):
        assert finding_identity(original['originalFinding']) == finding_identity(finding)
        path = original['path']
        assert original['sourceSha256'] == prior[path] and static['sourceHashes'][path] == hashes[path]
        assert original['dynamicQualification'] is False
        rebinding.append(dict(originalMetadataId=original['metadataId'],originalSource=BASE,source=SOURCE,
            path=path,sourceSha256=hashes[path],currentFinding=finding,reason=original['reason'],
            disposition='NOT_APPLICABLE_TO_EXACT_TEST_CONTEXT',dynamicQualification=False,
            basis='EXACT_SOURCE_RESTORE_AND_CURRENT_RAW_FINDING_IDENTITY_NOT_RUNTIME_TRANSFER'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in review['companionSourceHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'current-contexts.json',rebinding)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,baseSource=BASE,invocation=invocation,
        sourceChanges=bindings,compileManifestSha256=data.sha(normal_path.read_bytes()),
        sourcePlanSha256=data.sha((data.BASE/'PG10628-query-semantic-constant-plan-v1/manifest.json').read_bytes()),
        currentStaticSha256=data.sha((data.BASE/'PG10630-query-semantic-constant-static-v1/manifest.json').read_bytes()),
        oldStaticContextManifestSha256=data.sha(review_path.read_bytes()),currentContextsSha256=data.sha((OUT/'current-contexts.json').read_bytes()),
        mainClassesUnchanged=1843,otherTestClassesUnchanged=1962-len(byte_changes),physicalTestClassesChanged=len(byte_changes),
        changedTestClasses=[dict(module=m,entry=p) for m,p in byte_changes],totalTestClasses=1962,
        resultIdentifierRenamed=1,ordinalConstants=3,ordinalConditionReferences=5,independentMetadataNegativeVectors=negatives,
        actionableFindingsRemoved=5,remainingRawFindings=34,currentContextNotApplicable=34,
        rawStaticExit=1,suppressionsAdded=False,actualExecutorShutdownLivenessProven=False,
        productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,
        externalActions=0,oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
