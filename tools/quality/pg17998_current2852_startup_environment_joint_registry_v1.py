"""Two pure StartupInputs wrappers close to natural branch N/A; quality2 plus necessary input8."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from trace_owner_join import canonical

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV = ('PG17978-current2850-pure-retirement-joint-registry-v1','a26ab8e71f29f594a80d960d6ad4ce72e5362ef798ee6526aed3fe78e6dbd7a2')
PREV_POST = ('PG17980-current2850-pure-retirement-joint-registry-post-v1','b32de2e4feea485b008d4768fa052ee724c52bb276ccae7df9f4df71ca18a423')
JOINT = ('PG17992-startup-environment-ten-post-v1','7ab47d6e2acfdf8fd9da99c99d11884b0174b94cf001ea986c6f6fea3d20f4da')
JOINT_POST = ('PG17994-startup-environment-ten-independent-v1','dab38e25f9b33aa6c5713859d271e415e44d60fb1e87875446f64260dae2f427')
REPLACED = {'dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs','dev/codex/schubert/nk/web/bootstrap/WebStartupInputs'}
OUT = data.BASE / 'PG17998-current2852-startup-environment-joint-registry-v1'

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
    require(proof['postSha256'] == JOINT[1] and proof['tests'] == 10 and proof['newUniqueMethods'] == 2 and proof['requiredRepeatedMethods'] == 8 and proof['semanticNegativeVectors'] == 32 and proof['independentOracleVectors'] == 10, 'exact independent27/new3/repeat24')
    require(p['singleSession'] is True and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0 and p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False, 'single genuine exec, no old coverage union')
    result = copy.deepcopy(old)
    old_cases = {(c['classname'], c['name']) for c in old['cases']}
    local = {(c['classname'], c['name']) for c in p['cases']}
    new, repeated = local - old_cases, local & old_cases
    require(len(local) == 10 and len(new) == 2 and len(repeated) == 8 and {c for c,name in new}=={'dev.codex.schubert.nk.api.bootstrap.ApiEnvironmentGateContractTest','dev.codex.schubert.nk.web.bootstrap.WebEnvironmentGateContractTest'} and {c for c,name in repeated}=={'dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest','dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest'}, 'all exact new/repeated original identities')
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
    quality_paths={'tools/quality/architecture/ApiEnvironmentGateContractTest.java':'0f6d43bd4e7b96046cd4acae44f9cbcdb58f97c76befcee3701afcb0d0ed40a2','tools/quality/architecture/WebEnvironmentGateContractTest.java':'f62b8d2f648950b7e76edced38b81e17f03bfe1bccf941ce696937c742d656d7'}
    for quality_path,quality_sha in quality_paths.items():
        require(quality_path not in result['owners'] and proof['originalTestSourceHashes'][quality_path]==quality_sha==data.sha((data.ROOT/quality_path).read_bytes()),'exact quality hash separate from production owners')
        result['additionalScopeReferences'].append(dict(name=JOINT[0],sha256=JOINT[1],independentPost=list(JOINT_POST),scope='QUALITY_TOOL_INJECTED_ENVIRONMENT_NOT_PRODUCTION_OWNER',qualityToolPath=quality_path,qualityToolSha256=quality_sha,referenceOnly=True,newTests=0,newExecs=0,newUniqueMethodsDeclaredByJoint=1,changeOwner='WBS-F03',canonicalOwner=None,canonicalCostOwner=None,additionalSharedCostPp=0,actualAllocatedPp=None))
    for name in p['metadataClasses']:
        require(result['metadataClasses'][name]['sha256'] == p['physicalClasses'][name], 'same old NoCode bytes preserved, not newly added')
    result['jointQualificationReplacedUnitHistory'].update(history)
    reference = dict(post=list(JOINT), independentPost=list(JOINT_POST), originalMethods=10, newUniqueMethods=2, necessaryRepeatedMethods=8, originalProductJvms=1, countedInOriginalExecs=True, coverageExecUnion=False, purpose='ONE_EXEC_ENVIRONMENT_QUALITY2_NECESSARY_INPUTS8_SOURCE2_NATURAL_BRANCH_ZERO_NOT_NATIVE_ADMISSION')
    result['jointQualificationReferences'].append(reference)
    result['originalPostReferences'].append(dict(name=JOINT[0], sha256=JOINT[1], tests=10, suites=4, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope='JOINT_NEW_QUALITY2_NECESSARY_ORIGINAL_REPEAT8_SOURCE2_NATURAL_BRANCH_NA_NO_EXEC_UNION'))
    cases = old_cases | local
    physical = {c for u in units.values() for c in u['physical']}
    four = {c for u in units.values() if u['four100'] for c in u['physical']}
    natural = {c for u in units.values() if u['branchNaturallyZero'] for c in u['physical']}
    metadata = result['metadataClasses']
    incomplete = {n for n, u in units.items() if not (u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(physical) == sum(len(u['physical']) for u in units.values()), 'no shared physical class counters')
    result.update(invocation=invocation, previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}),
        originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + 10,
        uniqueProductMethodDelta=2, newTestIds=2, sourceProgramDelta=0, measuredSourcePrograms=len(units), measuredPhysical=len(physical), executablePhysical=len(physical - metadata.keys()),
        four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - metadata.keys()),
        naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()), naturalZeroBranchPhysical=len(natural), incompleteSourcePrograms=len(incomplete),
        ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())), unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),
        necessaryJointRepeatedMethods=old['necessaryJointRepeatedMethods'] + 8, totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods'] + 8)
    require((result['tests'], result['suites'], len(units), len(physical), result['executablePhysical'], result['four100SourcePrograms'], len(four), result['four100ExecutablePhysical'], result['naturalZeroBranchSourcePrograms'], len(natural), len(incomplete), result['totalProductExecs'], result['totalMethodExecutions'], result['totalRepeatedOriginalMethods']) == (2852,429,588,1021,823,298,443,418,187,204,80,218,3007,155), 'all current unique/repeat/whole Source counters')
    require(result['ownerStatusCounts'] == {'BASELINE_LOGICAL_REFERENCE':523,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':236,'UNKNOWN':302}, 'exact responsibilities, no change-owner promotion')
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    declaration = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', declaration['files']['exact-ordinary-bindings.json'])
    keys = {(b['className'], b['method']) for b in bindings}
    require(len(cases & keys) == 2806 and len(cases - keys) == 46, 'ordinary declarations and six quality fixture cases stay separate')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=46)
    result['currentOrdinaryTestDeclarationReference'] = decl
    changed = {'invocation', 'previousUniqueRegistryReference', 'previousRegistryPostReference', 'cases', 'suiteNames', 'tests', 'suites', 'originalExecs', 'totalProductExecs', 'totalMethodExecutions', 'uniqueProductMethodDelta', 'newTestIds', 'sourceProgramDelta', 'measuredSourcePrograms', 'measuredPhysical', 'executablePhysical', 'four100SourcePrograms', 'four100Physical', 'four100ExecutablePhysical', 'naturalZeroBranchSourcePrograms', 'naturalZeroBranchPhysical', 'incompleteSourcePrograms', 'ownerStatusCounts', 'unknownOwnerPaths', 'necessaryJointRepeatedMethods', 'totalRepeatedOriginalMethods', 'fullSourceUnits', 'owners', 'jointQualificationReplacedUnitHistory', 'jointQualificationReferences', 'additionalScopeReferences', 'originalPostReferences', 'currentOrdinaryTestDeclarationReference'}
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
