"""Replace one partial value proof with a whole new-fixture exec, preserving all old histories."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV = ('PG15978-current2091-expiry-joint-registry-v1', '6cc07d3fb25ccebaf5a406c85f401b49f83d127cb0811283ee0cd19d9de02862')
PREV_POST = ('PG15980-current2091-expiry-joint-registry-post-v1', '173392f2522ac3218d3848da298bf857f2cc314a3d2be1533e22096c8efa24de')
POST = ('PG15990-run-references-truth-table-three-post-v1', 'adef4b2453d8dcd84972f559419f5fb7538c9fd3ba8751d491c493b7d7a78a17')
INDEPENDENT = ('PG15992-run-references-truth-table-independent-v1', '211bd868869c1565261aa226cc688c9d924ae622aed847006f9421e923958997')
NAME = 'dev/codex/schubert/nk/batch/repository/RunReferences'
OUT = data.BASE / 'PG15994-current2094-reference-value-registry-v1'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def read(pair):
    return data.read_checked(data.BASE / pair[0] / 'manifest.json', pair[1])

def wire(value):
    return json.dumps(value, sort_keys=True)

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    old, prior, p, q = [read(v) for v in (PREV, PREV_POST, POST, INDEPENDENT)]
    require(all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (old, prior, p, q)) and prior['registryManifestSha256'] == PREV[1] and q['postSha256'] == POST[1] and q['semanticNegativeVectors'] == 23 and q['independentOracleNegativeVectors'] == 5, 'same source and exact independent truth table')
    require(p['targetUnitFour100'] is q['onlyPublicBooleanTruthTableFixture'] is True and p['singleSession'] is True and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0 and p['metadataClasses'] == [], 'whole primitive Source and session')
    result = copy.deepcopy(old)
    cases = {(r['classname'], r['name']) for r in old['cases']}
    added = {(r['classname'], r['name']) for r in p['cases']}
    require(len(added) == 3 and not added & cases and all(c == 'dev.codex.schubert.nk.batch.repository.RunReferencesTruthTableTest' for c, n in added), 'new fixture three, not ordinary Source declarations')
    require(set(p['fullSourceUnits']) == {NAME} and NAME in old['fullSourceUnits'] and not old['fullSourceUnits'][NAME]['four100'] and NAME not in old['qualificationReplacedUnitHistory'], 'one declared incomplete value Source only')
    unit = p['fullSourceUnits'][NAME]
    previous = old['fullSourceUnits'][NAME]
    require(previous['physical'] == unit['physical'] == [NAME] and unit['four100'] is True, 'same complete physical identity')
    for kind in ('LINE', 'METHOD', 'CLASS', 'BRANCH'):
        before, after = previous['counters'][kind], unit['totals'][kind]
        require(before['covered'] + before['missed'] == after['covered'] + after['missed'] and after['missed'] == 0 and after['covered'] > 0, 'same denominator genuinely full, never exec union')
    result['qualificationReplacedUnitHistory'][NAME] = copy.deepcopy(previous)
    result['fullSourceUnits'][NAME] = dict(post=POST[0], postSha256=POST[1], physical=[NAME], counters=copy.deepcopy(unit['totals']), four100=True, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=False)
    require(all(path in old['owners'] and old['owners'][path] == row for path, row in p['owners'].items()), 'actual same baseline owner/cost, no new fixture reassignment')
    fixture_reference = dict(post=list(POST), independentPost=list(INDEPENDENT), source=SOURCE,
        fixture='tools/quality/architecture/RunReferencesTruthTableTest.java', fixtureSha256='57eb6860f5767a5e8c2967899f4cce13437e5c1a05fb19f4cbc313adcd628b57',
        tests=3, newUniqueMethods=3, necessaryRepeatedMethods=0, normalOrdinaryTestSourceDomain=False,
        wholeSourceReplaced=NAME, countedInOriginalExecs=True, coverageExecUnion=False)
    require('valueFixtureQualificationReferences' not in result, 'first explicit value fixture replacement domain')
    result['valueFixtureQualificationReferences'] = [fixture_reference]
    result['originalPostReferences'].append(dict(name=POST[0], sha256=POST[1], tests=3, suites=1, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope='NEW_INDEPENDENT_PRIMITIVE_BOOLEAN16_QUALITY_FIXTURE3_ONE_COMPLETE_SOURCE_NOT_NORMAL_TEST_DECLARATIONS'))
    cases |= added
    units = result['fullSourceUnits']
    physical = {c for u in units.values() for c in u['physical']}
    four = {c for u in units.values() if u['four100'] for c in u['physical']}
    meta = result['metadataClasses']
    result.update(invocation=invocation, previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}), originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + 3, uniqueProductMethodDelta=3, newTestIds=3, sourceProgramDelta=0, four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - meta.keys()), incompleteSourcePrograms=sum(not (u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()))
    require(len(physical) == sum(len(u['physical']) for u in units.values()) == old['measuredPhysical'] == 654, 'no added or omitted Source/class')
    require((result['tests'], result['suites'], len(units), len(four), result['four100SourcePrograms'], result['four100ExecutablePhysical'], result['incompleteSourcePrograms'], result['totalProductExecs'], result['totalMethodExecutions'], result['totalRepeatedOriginalMethods']) == (2094, 278, 473, 366, 252, 355, 39, 124, 2226, 132), 'exact one-Source closure and unique/JVM counts')
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    declarations = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', declarations['files']['exact-ordinary-bindings.json'])
    keys = {(b['className'], b['method']) for b in bindings}
    require(len(cases & keys) == 2085 and len(cases - keys) == 9 and not added & keys, 'new quality fixtures never count as normal declarations')
    decl.update(existingQualityFixtureCases=9)
    result['currentOrdinaryTestDeclarationReference'] = decl
    changed = {'invocation', 'previousUniqueRegistryReference', 'previousRegistryPostReference', 'cases', 'suiteNames', 'tests', 'suites', 'originalExecs', 'totalProductExecs', 'totalMethodExecutions', 'uniqueProductMethodDelta', 'newTestIds', 'sourceProgramDelta', 'four100SourcePrograms', 'four100Physical', 'four100ExecutablePhysical', 'incompleteSourcePrograms', 'fullSourceUnits', 'qualificationReplacedUnitHistory', 'originalPostReferences', 'currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k]) == wire(v) for k, v in old.items() if k not in changed) and all(result['fullSourceUnits'][n] == u for n, u in old['fullSourceUnits'].items() if n != NAME) and all(result['qualificationReplacedUnitHistory'][n] == u for n, u in old['qualificationReplacedUnitHistory'].items()), 'all original Catalog/joint/corrections/owner/cost/formal fields preserved')
    require(result['ownerStatusCounts'] == dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())), 'all old responsibilities unchanged')
    for value in (old, prior, p, q):
        verify(value['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', result)
    print(data.sha((OUT / 'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
