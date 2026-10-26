"""Independent literal restoration and exact current static/source-byte scope; no Graph execution."""
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from public_java_digest_provenance import LEX
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg10690_current_global_static_post import finding_rows

OUT = data.BASE/'PG10718-graph-constants-source-post-v1'
SOURCE = '68278a0402137b8f27c3714d6d3c00848ccf0f49'


def restore(text,constants):
    table = {}
    for row in constants:
        name,value,count = row['name'],row['literal'],row['references']
        pattern = r'\bprivate\s+static\s+final\s+String\s+'+re.escape(name)+r'\s*=\s*'+re.escape(value)+r'\s*;'
        if len(re.findall(pattern,text)) != 1:
            raise ValueError('one exact same-value constant declaration required')
        text = re.sub(pattern,'',text,count=1)
        if sum(m.group() == name for m in LEX.finditer(text)) != count:
            raise ValueError('all exact Test constant references required')
        table[name] = value
    return canonical(' '.join(table.get(m.group(),m.group()) for m in LEX.finditer(text)
        if not m.group().startswith(('//','/*'))))


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan_path = data.BASE/'PG10711-graph-diagnostic-formatted-plan-v1/manifest.json'
    plan = data.read_checked(plan_path,'43acb8f26d836d7027efd7d5fa0e9567df4dcd1d10c12cd390efc31fd9679439')
    old = data.read_checked(data.BASE/'PG10698-graph-import-six-compile-v1/manifest.json',
        '7177fe941af4b6df2f2237112b0f3cc5eb9a82f21f8ef22c34eca6674eec1338')
    normal_path = data.BASE/'PG10714-graph-constants-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    static_path = data.BASE/'PG10716-graph-constants-static-v1/manifest.json'
    static = json.loads(static_path.read_bytes())
    assert normal['source'] == static['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == static['actualExit'] == 0
    hashes,previous = normal['begin']['inputHashes'],old['begin']['inputHashes']
    changes = {r['path']:r for r in plan['sourceChanges']}
    assert set(hashes) == set(previous) and {p for p in hashes if hashes[p] != previous[p]} == set(changes) and len(changes) == 3
    snapshot = Path(old['jars']['api']['path']).parent.parent.parent.parent
    bindings,negatives = [],0
    for path,row in changes.items():
        before = (snapshot/path).read_text()
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == previous[path] == row['beforeSha256']
        assert data.sha(after.encode()) == hashes[path] == row['sha256'] == static['sourceHashes'][path]
        assert restore(after,row['constants']) == canonical(before)
        first = row['constants'][0]
        damaged = after.replace(first['literal'],'"CHANGED"',1)
        assert damaged != after
        try:
            restore(damaged,row['constants'])
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('different constant value accepted')
        assert restore(after.replace('assertSame(', 'assertEquals(',1),row['constants']) != canonical(before)
        negatives += 1
        bindings.append(dict(path=path,beforeSha256=previous[path],sha256=hashes[path]))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert jar_classes(old) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test,new_test = test_classes(old),test_classes(normal)
    assert set(old_test) == set(new_test) and len(new_test) == 1962
    byte_changes = sorted(k for k in new_test if new_test[k] != old_test[k])
    allowed = {(p.split('/')[1].removeprefix('schubert-nk-'),p.split('/src/test/java/')[1].removesuffix('.java')) for p in changes}
    for module,entry in byte_changes:
        stem = entry.removesuffix('.class').split('$')[0]
        assert (module,stem) in allowed
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/entry
        assert decode(file.read_bytes(),entry)['sourceFile'] == stem.rpartition('/')[2]+'.java'
    global_path = data.BASE/'PG10690-current-global-static-post-v1/manifest.json'
    global_meta = data.read_checked(global_path,'465c7c64bc75923d275436c72656ddc5b537f2c15982a71a0b4681a19ef03627')
    prior_rows = data.read_checked(global_path.parent/'findings.json',global_meta['findingsSha256'])
    removed = [r for r in prior_rows if r['path'] in changes]
    assert len(removed) == 7 and sum(r['scanner'] == 'pmd' for r in removed) == 4
    unchanged = [r for r in prior_rows if r['path'] not in changes]
    assert len(unchanged) == 9402 and all(r['inputSha256'] == hashes[r['path']] for r in unchanged)
    for label in ('pmd','checkstyle'):
        raw = (static_path.parent/(label+'.xml')).read_bytes()
        assert data.sha(raw) == static['reports'][label]['sha256']
        rows,_ = finding_rows(raw,label,static['sourceHashes'])
        assert not rows and static['reports'][label]['findings'] == static['reports'][label]['processingErrors'] == 0
        assert static['stages'][label]['actualExit'] == 0 and not static['stages'][label]['timedOut']
    assert negatives == 6
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'current-source-finding-delta.json',dict(originalIndexManifestSha256=data.sha(global_path.read_bytes()),
        removedByChangedSourceIds=[r['id'] for r in removed],newSubsetPmdFindings=0,newSubsetCheckstyleFindings=0,
        unchangedSourceFindingCount=9402,unchangedSourceInputsMatchCurrent=True,
        qualification='SOURCE_BOUND_FINDING_DELTA_NOT_FULL_CURRENT_SOURCE_SCANNER_RERUN_OR_GATE_PASS'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,baseSource=old['source'],invocation=invocation,
        sourceChanges=bindings,compileManifestSha256=data.sha(normal_path.read_bytes()),staticManifestSha256=data.sha(static_path.read_bytes()),
        sourcePlanSha256=data.sha(plan_path.read_bytes()),mainClassesUnchanged=1843,totalTestClasses=1962,
        otherTestClassesUnchanged=1962-len(byte_changes),physicalTestClassesChanged=len(byte_changes),
        changedTestClasses=[dict(module=m,entry=p) for m,p in byte_changes],constantsAdded=4,literalReferencesReplaced=20,
        independentMetadataNegativeVectors=6,removedApplicablePmdFindings=4,currentSubsetStaticExit=0,
        sourceFindingDeltaSha256=data.sha((OUT/'current-source-finding-delta.json').read_bytes()),
        unchangedSourceFindingCount=9402,wholeF03Accepted=False,changedClassInstructionsIndividuallyCompared=False,
        productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,externalActions=0,
        oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
