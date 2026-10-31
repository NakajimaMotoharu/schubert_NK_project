"""One-exec Expiry proof replacement. Unique3/repeat24, old histories and costs preserved."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from trace_owner_join import canonical

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV = ('PG15962-current2088-expiry-scope-registry-v1', 'fe4e0cd55f6677b6797dea4644781ec91ee99a3c2c9597ed8712917f55c7393f')
PREV_POST = ('PG15964-current2088-expiry-scope-registry-post-v1', '52c3e65009c41e17c1649597d7d3f572ef8791bf69223bc2d43d8b13bb51bb4c')
JOINT = ('PG15974-expiry-jdbc-joint27-post-v1', '5e1a62e0b3d9fa7dc9cac16b2bfb34be70ceac4f5e15aa986ddff847076e3b53')
JOINT_POST = ('PG15976-expiry-jdbc-joint27-independent-v1', 'd6c990057492491e2bbe3221e9c7161510537447bb068d6458063a6b294d22d1')
REPLACED = {'dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository', 'dev/codex/schubert/nk/batch/repository/BatchRepositoryException'}
OUT = data.BASE / 'PG15978-current2091-expiry-joint-registry-v1'

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
    old, prior, p, proof = [read(v) for v in (PREV, PREV_POST, JOINT, JOINT_POST)]
    require(all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (old, prior, p, proof)) and prior['registryManifestSha256'] == PREV[1], 'same current source genuine inputs')
    require(proof['postSha256'] == JOINT[1] and proof['tests'] == 27 and proof['newUniqueMethods'] == 3 and proof['requiredRepeatedMethods'] == 24 and proof['semanticNegativeVectors'] == 27 and proof['independentFaultMatrixRows'] == 68, 'exact independent27/new3/repeat24')
    require(p['singleSession'] is True and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0 and p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False, 'single genuine exec, no old coverage union')
    result = copy.deepcopy(old)
    old_cases = {(c['classname'], c['name']) for c in old['cases']}
    local = {(c['classname'], c['name']) for c in p['cases']}
    new, repeated = local - old_cases, local & old_cases
    require(len(local) == 27 and len(new) == 3 and len(repeated) == 24 and all(c.endswith('.ExpiryAuditResourceFailureTest') for c, name in new) and all(c.endswith('.ExpirySuccessfulScopeTest') for c, name in repeated), 'all exact new/repeated original identities')
    units = result['fullSourceUnits']
    require(set(units) & set(p['fullSourceUnits']) == REPLACED and not REPLACED & set(result['jointQualificationReplacedUnitHistory']), 'only two declared old proofs superseded, all prior histories disjoint')
    history = {n: copy.deepcopy(units[n]) for n in REPLACED}
    for name, unit in p['fullSourceUnits'].items():
        if name in REPLACED:
            previous = units[name]
            require(previous['physical'] == unit['physical'], 'same whole Source physical identity')
            for kind in ('LINE', 'METHOD', 'CLASS', 'BRANCH'):
                a, b = previous['counters'][kind], unit['totals'][kind]
                require(a['covered'] + a['missed'] == b['covered'] + b['missed'] and b['covered'] >= a['covered'] and b['missed'] <= a['missed'], 'same denominator monotone joint measurement, never merged')
        units[name] = dict(post=JOINT[0], postSha256=JOINT[1], physical=copy.deepcopy(unit['physical']), counters=copy.deepcopy(unit['totals']), four100=unit['four100'], execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=unit['branchNaturallyZero'] and unit['threeCounter100'])
    normal = read(('PG14216-typed-marker-guard-six-compile-v1', old['normalManifestSha256']))
    hashes = normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT / path).read_bytes()) == digest for path, digest in hashes.items()), 'all fixed current inputs unchanged')
    logical = {r['path']: r for r in json.loads((data.ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path, owner in p['owners'].items():
        require(owner['sha256'] == hashes[path] and all(owner[k] == v for k, v in canonical(path, logical).items()), 'exact old canonical/UNKNOWN file owners')
        require(path not in result['owners'] or result['owners'][path] == owner, 'shared owner bytes/meaning unchanged')
        result['owners'][path] = copy.deepcopy(owner)
    for name in p['metadataClasses']:
        require(result['metadataClasses'][name]['sha256'] == p['physicalClasses'][name], 'same old NoCode bytes preserved, not newly added')
    result['jointQualificationReplacedUnitHistory'].update(history)
    reference = dict(post=list(JOINT), independentPost=list(JOINT_POST), originalMethods=27, newUniqueMethods=3, necessaryRepeatedMethods=24, originalProductJvms=1, countedInOriginalExecs=True, coverageExecUnion=False, purpose='ONE_EXEC_EXPIRY_READ_AND_REQUIRED_SUCCESS_PREDICATE_TWR_SCOPE_IMPROVEMENT_NOT_WHOLE_PROGRAM_ACCEPTANCE')
    result['jointQualificationReferences'].append(reference)
    result['originalPostReferences'].append(dict(name=JOINT[0], sha256=JOINT[1], tests=27, suites=2, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope='JOINT_ORIGINAL3_AND_NECESSARY_REPEAT24_FIVE_WHOLE_SOURCE_SCOPE_NO_EXEC_UNION'))
    cases = old_cases | local
    physical = {c for u in units.values() for c in u['physical']}
    four = {c for u in units.values() if u['four100'] for c in u['physical']}
    natural = {c for u in units.values() if u['branchNaturallyZero'] for c in u['physical']}
    metadata = result['metadataClasses']
    incomplete = {n for n, u in units.items() if not (u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical) == sum(len(u['physical']) for u in units.values()), 'no shared physical class counters')
    result.update(invocation=invocation, previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}),
        originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + 27,
        uniqueProductMethodDelta=3, newTestIds=3, sourceProgramDelta=3, measuredSourcePrograms=len(units), measuredPhysical=len(physical), executablePhysical=len(physical - metadata.keys()),
        four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - metadata.keys()),
        naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()), naturalZeroBranchPhysical=len(natural), incompleteSourcePrograms=len(incomplete),
        ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())), unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),
        necessaryJointRepeatedMethods=old['necessaryJointRepeatedMethods'] + 24, totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods'] + 24)
    require((result['tests'], result['suites'], len(units), len(physical), result['executablePhysical'], result['four100SourcePrograms'], len(four), result['four100ExecutablePhysical'], result['naturalZeroBranchSourcePrograms'], len(natural), len(incomplete), result['totalProductExecs'], result['totalMethodExecutions'], result['totalRepeatedOriginalMethods']) == (2091, 277, 473, 654, 615, 251, 365, 354, 176, 191, 40, 123, 2223, 132), 'all current unique/repeat/whole Source counters')
    require(result['ownerStatusCounts'] == {'BASELINE_LOGICAL_REFERENCE': 388, 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED': 229, 'UNKNOWN': 161}, 'exact responsibilities, no change-owner promotion')
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    declaration = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', declaration['files']['exact-ordinary-bindings.json'])
    keys = {(b['className'], b['method']) for b in bindings}
    require(len(cases & keys) == 2085 and len(cases - keys) == 6, 'ordinary declarations and six quality fixture cases stay separate')
    decl.update(ordinaryCaseReferences=2085, ordinaryWithoutCurrentCaseReference=3701)
    result['currentOrdinaryTestDeclarationReference'] = decl
    changed = {'invocation', 'previousUniqueRegistryReference', 'previousRegistryPostReference', 'cases', 'suiteNames', 'tests', 'suites', 'originalExecs', 'totalProductExecs', 'totalMethodExecutions', 'uniqueProductMethodDelta', 'newTestIds', 'sourceProgramDelta', 'measuredSourcePrograms', 'measuredPhysical', 'executablePhysical', 'four100SourcePrograms', 'four100Physical', 'four100ExecutablePhysical', 'naturalZeroBranchSourcePrograms', 'naturalZeroBranchPhysical', 'incompleteSourcePrograms', 'ownerStatusCounts', 'unknownOwnerPaths', 'necessaryJointRepeatedMethods', 'totalRepeatedOriginalMethods', 'fullSourceUnits', 'owners', 'jointQualificationReplacedUnitHistory', 'jointQualificationReferences', 'originalPostReferences', 'currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k]) == wire(v) for k, v in old.items() if k not in changed), 'all unrelated cost/authority/formal/history fields immutable')
    require(all(units[n] == u for n, u in old['fullSourceUnits'].items() if n not in REPLACED) and all(result['jointQualificationReplacedUnitHistory'][n] == u for n, u in old['jointQualificationReplacedUnitHistory'].items()), 'all unrelated Source and old joint histories retained')
    for value in (old, prior, p, proof):
        verify(value['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', result)
    print(data.sha((OUT / 'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
