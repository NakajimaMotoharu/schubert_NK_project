"""Bind the exact five P004-03 artifacts to current sources and separately scoped evidence."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import gzip
import json
import runpy
from xml.etree import ElementTree as ET

ENTRY = Path(__file__).resolve()
h = runpy.run_path(str(ENTRY.with_name('5189_wbs66_four_module_delta_handoff.py')))
E = h['E']
D = h['D']
OUT = E / 'PG39700-p00403-five-artifacts-current-lineage-v1'
PMO = D.parent
WBS = 'WBS-P004-03'
PROTOCOL = 'dev.codex.schubert.nk.'
SOURCE = 'src/schubert-nk-batch/src/'


def find_plan(item):
    if isinstance(item, dict):
        if item.get('id') == WBS:
            yield item
        for v in item.values():
            yield from find_plan(v)
    elif isinstance(item, list):
        for v in item:
            yield from find_plan(v)


def evidence(prefix):
    return h['matching_path'](prefix + '*/manifest.json')


def sha_git(source, path):
    return h['sha'](h['git']('show', f'{source}:{path}'))


def file_hashes(post, names):
    refs = [h['ref'](post.parent / n) for n in names]
    evidence = h['load'](post)
    for r in refs:
        assert r['sha256'] == evidence['files'][Path(r['path']).name]
    return refs


def exact_xml(path, expected):
    cases = ET.parse(path).getroot().findall('testcase')
    assert len(cases) == expected
    assert not any(case.findall('skipped') or case.findall('failure') or case.findall('error') for case in cases)
    return sorted((c.get('classname'), c.get('name')) for c in cases)


def codec_proof(current, head, compiled):
    criteria = evidence('PG37288')
    source = h['load'](criteria)
    post = h['revalidate_reference'](source['post'])
    assert source['actualExit'] == post['actualExit'] == 0 and source['allRawCounters100']
    assert post['tests'] == source['tests'] == 20 and not any(post[k] for k in ('failed','errors','skipped','notRun'))
    inputs = h['revalidate_reference'](post['prepare'])['inputHashes']
    bound = {p: value for p, value in inputs.items() if '/src/test/' in p}
    assert len(bound) == 4 and all(sha_git(head, p) == v for p, v in bound.items())
    qualified = source['completeClassSha256']
    assert len(qualified) == 6
    assert all(compiled[name + '.class'] == sha for name, sha in qualified.items())
    refs = file_hashes(Path(source['post']['path']), ['TEST-junit-jupiter.xml', 'jacoco.exec', 'unfiltered.stdout'])
    raw = next(row for row in refs if row['path'].endswith('TEST-junit-jupiter.xml'))
    observed = exact_xml(Path(raw['path']), 20)
    assert set(observed) == {tuple(row) for row in post['actualExpectedCases']}
    assert all(h['ref'](Path(r['path']))['sha256'] == r['sha256'] for r in source['wire'])
    exact_main = [p for p in inputs if p.endswith('/MaintenanceRecords.java') or p.endswith('/MaintenanceRetirement.java')]
    assert len(exact_main) == 2 and all(sha_git(current, p) == inputs[p] for p in exact_main)
    return dict(proof=h['ref'](criteria), originalPost=source['post'], testCases=20, originalLiveExecution=False,
                unitSource=post['source'], coreSource=post['sourceCore'], testPins=bound, physicalPins=qualified,
                usefulScopes=['Public MaintenanceRecords and MaintenanceRetirement value codec'],
                trace=[h['ref'](Path(r['path'])) for r in source['wire']], measurements=refs,
                usableCurrentTarget='LOCAL_ARTIFACT_BYTE_IDENTICAL_NO_NEW_EXEC_OR_WHOLE_RECOGNITION')


def dao_proof(current, head, compiled):
    receipt = evidence('PG38688')
    source = h['load'](receipt)
    post = h['revalidate_reference'](source['post'])
    config = h['revalidate_reference'](post['config'])
    preflight = h['revalidate_reference'](post['preflight'])
    prepare = h['revalidate_reference'](preflight['prepare'])
    assert source['tests'] == post['tests'] == config['expectedTests'] == 8
    assert source['actualExit'] == post['actualExit'] == 0 and source['targetCoverage100']
    assert not any(source[k] for k in ('notRun','failures','errors','skipped'))
    main = next(p for p in post['inputHashes'] if p.endswith('/RunReferenceRepository.java'))
    test = config['testSources'][0]['path']
    assert test.endswith('/RunReferenceRepositoryPureJdbcTest.java')
    assert post['inputHashes'][main] == sha_git(current, main) and post['inputHashes'][test] == sha_git(head, test)
    physical = prepare['physicalClassHashes']
    assert len(physical) == 9 and all(compiled[p] == v for p, v in physical.items())
    xml = source['xml']
    assert all(h['ref'](Path(row['path'])) == row for row in xml)
    assert h['ref'](Path(source['exec']['path'])) == source['exec']
    cases = exact_xml(Path(xml[0]['path']), 8)
    assert all(name.endswith('.RunReferenceRepositoryPureJdbcTest') for name, _ in cases)
    return dict(proof=h['ref'](receipt), originalPost=source['post'], originalCaseCount=8,
                unitSource=post['source'], coreSource=post['productionCoreMain'],
                targetRaw=source['targetCounters'], testPins={test: post['inputHashes'][test]},
                physicalPins=physical, coverage=source['exec'], xml=xml, nativeOrPolicyUsed=False,
                scope='RRF-PURE-001..008, SS332 closed borrowed Jdbc/UTC',
                actualDbFunctionOrAuthorizationQualified=False)


def required_native(current, head):
    receipt = evidence('PG38304')
    source = h['load'](receipt)
    assert source['currentTestCount'] is None and source['currentCoverage'] is None and source['newTestsRun'] == 0
    value = {}
    for row in source['currentQualifications']:
        for artifact in row['sourceFiles']:
            rel = artifact['path']
            version = current if '/src/main/' in rel else head
            assert sha_git(version, rel) == artifact['currentSourceSha256']
            assert not artifact['sameBytes']
        h['revalidate_reference'](row['oldLimitedRunResult'])
        assert row['owner'] == WBS
        report = dict(currentInputHashes=row['sourceFiles'], pastResult=row['oldLimitedRunResult'],
                      pastCases=len(row['historicalNamedCaseInvocations']), pastCoverageMiss=row['historicalScopeMisses'],
                      originalPlanRow=row['plannedSubrow'], originalPlanRowPrice=row['plannedPp'],
                      currentProductTests=None, currentNativeCoverage=None, verificationStatus='HOLD_EXACT_CURRENT_RUN_MISSING')
        value[row['target']] = report
    assert len(value) == 2
    return dict(priorAssessment=h['ref'](receipt), targets=value)


def physical_references(owners, compiled, binding):
    old = h['revalidate_reference'](binding['historicalBaseline'])
    archive = Path(binding['historicalBaseline']['path']).with_name('jdeps.stdout.gz')
    assert h['ref'](archive)['sha256'] == old['evidence'][archive.name]
    delta = Path(binding['rawAnalysis']['path'])
    assert h['ref'](delta) == binding['rawAnalysis']
    replacement = set(binding['changedAndNewPhysical']) | set(binding['removed'])
    before = h['edges'](gzip.decompress(archive.read_bytes()).decode())
    appeared = h['edges'](gzip.decompress(delta.read_bytes()).decode())
    rows = [(a, b, c) for a, b, c in before if a not in replacement] + appeared
    actual_map = {str(n).replace('/','.').removesuffix('.class') for n in compiled}
    refs = {n: set() for n in owners}
    for origin, dep, _ in rows:
        parent = origin.split('$', 1)[0]
        if parent in refs and dep.startswith(PROTOCOL):
            assert dep in actual_map
            refs[parent].add(dep)
    return {p: sorted(v) for p, v in refs.items()}


def main():
    start = h['load'](next(D.glob('480_*')))
    values = start['values']
    core, head = values['productionCoreMain'], values['source']
    assert h['git']('rev-parse','HEAD').decode().strip() == head
    assert h['git']('rev-parse','origin/dev-foundation').decode().strip() == head
    assert all(h['ref'](Path(v['path'])) == v for v in values['oracleReferences'])
    plan = next(PMO.glob('481_*'))
    [node] = list(find_plan(h['load'](plan)))
    owner_file = next(PMO.glob('485_*'))
    owners = [a for a in h['load'](owner_file)['artifacts'] if a['owner'] == WBS]
    assert len(owners) == 5 and set(node['ownedArtifacts']) == {row['path'] for row in owners}
    assert node['acceptance']['status'] == 'NOT_ACCEPTED' and node['sharedClassReferences'] == []
    build = h['matching_path']('PG39462*/compile/manifest.json')
    m = h['load'](build)
    assert m['actualExit'] == 0 and m['inputHashesReverified']
    assert all(sha_git(core, a['path']) == sha_git(head, a['path']) == m['sourceInputs'][a['path']]
               for a in owners)
    counters = Counter(i for m in m['physicalClassHashes'].values() for i in m)
    assert len(counters) == 1101 and max(counters.values()) == 1
    compiled = {i: key for classes in m['physicalClassHashes'].values() for i, key in classes.items()}
    relevant = {a['class'].replace('/','.') for a in owners}
    records = codec_proof(core, head, compiled)
    dao = dao_proof(core, head, compiled)
    native = required_native(core, head)
    physical = evidence('PG39616')
    evaluated = physical_references(relevant, compiled, h['load'](physical)['f02PhysicalEdges'])
    assert all(evaluated.values())
    rows = []
    for a in sorted(owners,key=lambda row:row['path']):
        path = a['path']; name = a['class']
        versions = {c: sha for c, sha in compiled.items() if c == name + '.class' or c.startswith(name + '$')}
        assert versions
        rows.append(dict(path=path, currentSourceSha=sha_git(core,path), canonicalOwner=a['owner'],
                         physicalClassPins=versions, directKnownProductTypeReferences=evaluated[name.replace('/','.')],
                         linkedScope='HELD' if path in native['targets'] else
                                     'JDBC_PORT_ONLY' if path.endswith('/RunReferenceRepository.java') else 'VALUE_CODEC_ONLY'))
    result = dict(actualExit=0, startEvent=start['eventId'], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  source=core, inspectedHead=head, plan=h['ref'](plan), ownerInventory=h['ref'](owner_file),
                  compileOriginal=h['ref'](build), requiredOwnedArtifacts=len(rows),
                  currentScopeArtifactTrace=rows, declaredSharedClassRefs=node['sharedClassReferences'],
                  physicalReferenceEvidence=h['ref'](physical), localValueEvidence=records, localJdbcEvidence=dao,
                  nativeOrActualFileEvidence=native, newProductTests=0, oldExecCombined=0,
                  currentWholeRawCoverage=None, liveDb=0, actualOwnedFileOperations=0,
                  newAcceptance=0, formalUpdated=False, whole451Accepted=False, effortRate=None,
                  requiredEnding=['Current native file open/held/terminal state for the two filesystem owners',
                                  'Authorized PostgreSQL function TABLE evidence and committed postconditions',
                                  'Current whole build/type gates F02/F03 and 451 with no actual trace gaps'],
                  currentTechnicalVerdict='FIVE_ARTIFACTS_BOUND_THREE_LOCAL_COMPONENTS_TWO_OPERATING_HOLDS',
                  verifier=h['ref'](ENTRY.relative_to(Path.cwd())))
    p = OUT / 'manifest.json'
    h['write'](p, result)
    print(h['ref'](p))


if __name__ == '__main__':
    main()
