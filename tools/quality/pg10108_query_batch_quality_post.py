"""Independent source-delta/old-oracle preservation, normal Main byte and static applicability join."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from public_java_digest_provenance import LEX
from pg10102_query_batch_preflight import NEW, PREFIX

SOURCE = 'dd138e9def675f9278ae4b1bdb8c5ee3e34f2b77'
OUT = data.BASE/'PG10108-query-batch-quality-post-v1'


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def without_additions(text, methods, question):
    values = tokens(text)
    for name in methods:
        opening = ['@','Test','void',name,'(',')','{']
        indices = [i for i in range(len(values)) if values[i:i+len(opening)] == opening]
        assert len(indices) == 1
        start = indices[0]
        depth = 1
        end = start+len(opening)
        while depth:
            assert end < len(values)
            if values[end] == '{': depth += 1
            elif values[end] == '}': depth -= 1
            end += 1
        values[start:end] = []
    constant = ['private','static','final','String','COLUMN_TOTAL','=','"total"',';']
    indices = [i for i in range(len(values)) if values[i:i+len(constant)] == constant]
    assert len(indices) == 1
    values[indices[0]:indices[0]+len(constant)] = []
    values = ['"total"' if v == 'COLUMN_TOTAL' else v for v in values]
    if question:
        addition = tokens('import dev.codex.schubert.nk.protocol.layout.semantic.NotificationErrorCode;')
        indices = [i for i in range(len(values)) if values[i:i+len(addition)] == addition]
        assert len(indices) == 1
        values[indices[0]:indices[0]+len(addition)] = []
    return values


def old_contract(candidate, previous):
    if candidate != previous:
        raise ValueError('prior oracle/code tokens changed outside declared additions/constant folding')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10100-query-batch-six-compile-v1/manifest.json',
        'a2a8eb62b574693a47e5ce82b830185a7db3fd41f4af61ba4341b598c5f8e3f3')
    previous = data.read_checked(data.BASE/'PG10076-question-sql-six-compile-v1/manifest.json',
        '9ba6f1fabcda3a665fd2222fd21a9c2c6095ae773ec1cb37b408374ae8bc287d')
    static = data.read_checked(data.BASE/'PG10098-query-batch-precommit-static-v2/manifest.json',
        '2d7a7a6d3e19809b001e25e268bdf731bc02541345b7d0efc1947567a1e664e4')
    pt = data.read_checked(data.BASE/'PG10106-query-batch-post-v1/manifest.json',
        'b83f269bd2f8573e5e9f10341ad4fc96d6b0a93589e98d0c11e66467c00f0b2d')
    assert normal['actualExit'] == previous['actualExit'] == pt['actualExit'] == 0
    assert normal['source'] == pt['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes,old_hashes = normal['begin']['inputHashes'],previous['begin']['inputHashes']
    assert set(hashes) == set(old_hashes)
    changes = {p:h for p,h in hashes.items() if h != old_hashes[p]}
    assert changes == static['sourceHashes'] and len(changes) == 3
    assert static['source'] is None and static['baseSource'] == previous['source']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 6 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    old_root = Path(previous['jars']['api']['path']).parents[3]
    rows = []
    selected = set()
    metadata_vectors = []
    for binary,methods in NEW.items():
        path = 'src/schubert-nk-api/src/test/java/'+binary.replace('.','/')+'.java'
        assert path in changes
        old_text = (old_root/path).read_text()
        assert data.sha((old_root/path).read_bytes()) == old_hashes[path]
        current_text = (data.ROOT/path).read_text()
        reduced = without_additions(current_text,methods,binary.startswith(PREFIX+'question.'))
        reference = tokens(old_text)
        old_contract(reduced,reference)
        for label,edit in (
            ('literal',lambda v:v.__setitem__(next(i for i,x in enumerate(v) if x.startswith('"')),'"different"')),
            ('identifier',lambda v:v.__setitem__(next(i for i,x in enumerate(v) if x == 'assertEquals'),'assertNull')),
            ('append',lambda v:v.append(';'))):
            altered = list(reduced)
            edit(altered)
            try: old_contract(altered,reference)
            except ValueError: metadata_vectors.append(binary+'#'+label)
            else: raise AssertionError('old source mutation accepted')
        rows.append(dict(path=path,previousSha256=old_hashes[path],currentSha256=hashes[path],
            originalSourceTokenDigest=data.sha(json.dumps(reference).encode()),
            addedMethods=list(methods),oldOracleTokensUnchanged=True))
        selected.update(('api',binary.replace('.','/')+suffix+'.class') for suffix in ('','$Call','$Jdbc'))
    applicable = []
    pmd_path = data.BASE/'PG10098-query-batch-precommit-static-v2/pmd.xml'
    assert data.sha(pmd_path.read_bytes()) == static['reports']['pmd']['sha256']
    for file in ET.parse(pmd_path).getroot().iter():
        if file.tag.rsplit('}',1)[-1] != 'file': continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        assert path in changes
        for violation in file:
            rule = violation.get('rule')
            line = int(violation.get('beginline'))
            source_line = (data.ROOT/path).read_text().splitlines()[line-1]
            if rule == 'UseProperClassLoader':
                assert '.class.getClassLoader()' in source_line
                reason = 'standalone public JDK-interface proxy, not JavaEE-managed code'
            else:
                assert rule == 'UseConcurrentHashMap' and 'parameters = new HashMap<>()' in source_line
                reason = 'per-method serial private fixture Map; parallel=false; no owned threads'
            applicable.append(dict(path=path,rule=rule,line=line,status='NON_APPLICABLE_CONTEXT',reason=reason))
    assert len(applicable) == 6 and all(sum(r['path'] == p for r in applicable) == 2 for p in changes)
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before,after = test_classes(previous),test_classes(normal)
    assert set(before) == set(after) and len(before) == 1931 and len(selected) == 9
    assert all(after[p] == h for p,h in before.items() if p not in selected)
    changed_class = [dict(module=p[0],name=p[1],beforeSha256=before[p],afterSha256=after[p]) for p in sorted(selected) if before[p] != after[p]]
    assert pt['tests'] == 52 and pt['suites'] == 7 and pt['newTestIds'] == 4
    assert len(pt['requestUnitsFour100']) == 3 and all(pt['requestUnitsFour100'].values())
    assert pt['forbiddenProductProbeHits'] == 0 and not pt['coverageUnion'] and not pt['targetUnitsFour100']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        changedSourceBindings=rows,oldOraclePreservationMetadataVectors=metadata_vectors,
        mainClassesUnchanged=1843,physicalTestClasses=1931,selectedTestClassScope=9,
        otherTestClassesByteIdentical=1922,selectedTestClassChanges=changed_class,
        rawStaticExit=1,rawPmdFindings=6,checkstyleFindings=0,individualApplicability=applicable,
        suppressionsAdded=False,currentJavaPaths=1803,currentMainPaths=965,currentTestPaths=838,
        currentSourceTests=52,newTestIds=4,relatedRegressionMethods=48,suites=7,units=pt['units'],
        allThreeRequestUnitsFour100=True,repositoryUnitsFour100=False,noCodeInterfaceNotMeasuredPass=True,
        productTestsReexecuted=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,
        formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,oldOracleMetadataVectors=len(metadata_vectors),mainUnchanged=1843,
        otherTestClassesByteIdentical=1922,selectedRawDifferences=len(changed_class),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
