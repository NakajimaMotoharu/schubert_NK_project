"""Independent XML/set/whole-Source replacement reconstruction; no test or analyzer replay."""
import collections
import copy
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg17825_current2827_admission_joint_registry_v2 import SOURCE, PREV, PREV_POST, JOINT, JOINT_POST, REPLACED, read, require, wire

PIN = '8110527ffbaa8152c358418fab5b113f48ec2568bde424778766d2a66c395d2c'
OUT = data.BASE / 'PG17826-current2827-admission-joint-registry-post-v1'

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    old, prior, p, proof, current = [read(v) for v in (PREV, PREV_POST, JOINT, JOINT_POST, ('PG17825-current2827-admission-joint-registry-v2', PIN))]
    require(all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (old, prior, p, proof, current)) and prior['registryManifestSha256'] == PREV[1] and proof['postSha256'] == JOINT[1] and proof['semanticNegativeVectors'] == 31, 'same current independently qualified references')
    local = []
    for filename, digest in p['xmlHashes'].items():
        raw = (data.BASE / JOINT[0] / filename).read_bytes()
        require(data.sha(raw) == digest, 'original returned XML hash')
        root = ET.fromstring(raw)
        require(all(int(root.get(k)) == 0 for k in ('failures', 'errors', 'skipped')) and int(root.get('tests')) == len(root.findall('testcase')), 'all original cases FES0')
        for case in root.findall('testcase'):
            require(not list(case), 'not skipped/failed/aborted')
            local.append((case.get('classname'), case.get('name')))
    old_cases = {(r['classname'], r['name']) for r in old['cases']}
    new, repeated = set(local) - old_cases, set(local) & old_cases
    cases = old_cases | set(local)
    require(len(local) == len(set(local)) == 5 and len(new) == 2 and len(repeated) == 3 and all(c.endswith('.WebHttpAdmissionWaitingContractTest') for c, n in new) and all(c.endswith('.WebHttpAdmissionTest') for c, n in repeated), 'all exact original/new/repeated case identities')
    expected = copy.deepcopy(old)
    units = expected['fullSourceUnits']
    history = {n: copy.deepcopy(units[n]) for n in REPLACED}
    require(set(units) & set(p['fullSourceUnits']) == REPLACED and not set(history) & set(expected['jointQualificationReplacedUnitHistory']) and p['singleSession'] is True and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0, 'only declared two replacements from one genuine exec')
    for name, unit in p['fullSourceUnits'].items():
        measured = {kind: {role: sum(p['executable'][physical]['counters'][kind][role] for physical in unit['physical'] if physical in p['executable']) for role in ('covered', 'missed')} for kind in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
        require(wire(measured) == wire(unit['totals']), 'whole physical Source independent aggregate')
        four = all(v['covered'] > 0 and v['missed'] == 0 for v in measured.values())
        natural = measured['BRANCH'] == {'covered': 0, 'missed': 0} and all(measured[k]['covered'] > 0 and measured[k]['missed'] == 0 for k in ('LINE', 'METHOD', 'CLASS'))
        require(unit['four100'] is four, 'actual measured strict four category')
        if name in history:
            previous = history[name]
            require(previous['physical'] == unit['physical'], 'same source physical denominator')
            for kind in measured:
                a, b = previous['counters'][kind], measured[kind]
                require(a['covered'] + a['missed'] == b['covered'] + b['missed'] and b['covered'] >= a['covered'] and b['missed'] <= a['missed'], 'joint proof improves/preserves exact denominator, no sums across execs')
        units[name] = dict(post=JOINT[0], postSha256=JOINT[1], physical=copy.deepcopy(unit['physical']), counters=measured, four100=four, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=natural)
    for path, owner in p['owners'].items():
        require(path not in expected['owners'] or expected['owners'][path] == owner, 'shared source owner unchanged')
        expected['owners'][path] = copy.deepcopy(owner)
    quality_path='tools/quality/architecture/WebHttpAdmissionWaitingContractTest.java'
    require(quality_path not in expected['owners'] and proof['originalTestSourceHashes'][quality_path]=='797e3809992d2e3b3a6aba9477b28e198970bd7c80a0c9f0519960f11b9deb78'==data.sha((data.ROOT/quality_path).read_bytes()),'quality tool hash separate from src owner namespace')
    expected['additionalScopeReferences'].append(dict(name=JOINT[0],sha256=JOINT[1],independentPost=list(JOINT_POST),scope='QUALITY_TOOL_REAL_WAIT_ORACLE_NOT_PRODUCTION_ARTIFACT_OWNER',qualityToolPath=quality_path,qualityToolSha256=proof['originalTestSourceHashes'][quality_path],referenceOnly=True,newTests=0,newExecs=0,newUniqueMethodsDeclaredByJoint=2,changeOwner='WBS-F03',canonicalOwner=None,canonicalCostOwner=None,additionalSharedCostPp=0,actualAllocatedPp=None))
    expected['jointQualificationReplacedUnitHistory'].update(history)
    reference = dict(post=list(JOINT), independentPost=list(JOINT_POST), originalMethods=5, newUniqueMethods=2, necessaryRepeatedMethods=3, originalProductJvms=1, countedInOriginalExecs=True, coverageExecUnion=False, purpose='ONE_EXEC_REAL_WAIT_TWO_QUALITY_AND_NECESSARY_ORIGINAL_THREE_FULL_ADMISSION_SOURCE_NOT_WHOLE_NATIVE_ACCEPTANCE')
    expected['jointQualificationReferences'].append(reference)
    expected['originalPostReferences'].append(dict(name=JOINT[0], sha256=JOINT[1], tests=5, suites=2, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope='JOINT_NEW_QUALITY2_NECESSARY_ORIGINAL_REPEAT3_ONE_FULL_SOURCE_NO_EXEC_UNION'))
    physical = {c for u in units.values() for c in u['physical']}
    four = {c for u in units.values() if u['four100'] for c in u['physical']}
    natural = {c for u in units.values() if u['branchNaturallyZero'] for c in u['physical']}
    meta = expected['metadataClasses']
    require(len(physical) == sum(len(u['physical']) for u in units.values()), 'disjoint source physical classes')
    expected.update(invocation=current['invocation'], previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}), originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + len(local), uniqueProductMethodDelta=len(new), newTestIds=len(new), sourceProgramDelta=len(units) - len(old['fullSourceUnits']), measuredSourcePrograms=len(units), measuredPhysical=len(physical), executablePhysical=len(physical - meta.keys()), four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - meta.keys()), naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()), naturalZeroBranchPhysical=len(natural), incompleteSourcePrograms=sum(not (u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()), ownerStatusCounts=dict(collections.Counter(r['ownershipStatus'] for r in expected['owners'].values())), unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in expected['owners'].values()), necessaryJointRepeatedMethods=old['necessaryJointRepeatedMethods'] + len(repeated), totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods'] + len(repeated))
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    declaration = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', declaration['files']['exact-ordinary-bindings.json'])
    keys = {(b['className'], b['method']) for b in bindings}
    require(len(keys) == 5786 and len(cases & keys) == 2806 and len(cases - keys) == 21, 'ordinary declarations never include six fixture cases')
    decl.update(ordinaryCaseReferences=len(cases & keys), ordinaryWithoutCurrentCaseReference=len(keys - cases),existingQualityFixtureCases=21)
    expected['currentOrdinaryTestDeclarationReference'] = decl
    def contract(value):
        require(wire(value) == wire(expected), 'all independently reconstructed counters/whole source/history/case domains')
    contract(current)
    require((len(cases), current['suites'], len(units), len(physical), current['four100SourcePrograms'], len(four), current['incompleteSourcePrograms'], current['totalProductExecs'], current['totalMethodExecutions'], current['totalRepeatedOriginalMethods']) == (2827,422,570,1003,292,437,87,212,2962,135), 'exact current classification, not acceptance')
    vectors = [('new-as-all27', 'tests', 2115), ('repeat-erased', 'necessaryJointRepeatedMethods', 24), ('repeat-inflated', 'totalRepeatedOriginalMethods', 156), ('JVM-double', 'totalProductExecs', 124), ('method-exec', 'totalMethodExecutions', 2199), ('history-erased', 'jointQualificationReplacedUnitHistory', {}), ('joint-proof-erased', 'jointQualificationReferences', []), ('Catalog-history', 'qualificationReplacedUnitHistory', {}), ('Catalog-proof', 'additionalQualificationReferences', []), ('physical', 'measuredPhysical', 651), ('four-physical', 'four100Physical', 364), ('four-code', 'four100ExecutablePhysical', 353), ('pending-erased', 'incompleteSourcePrograms', 0), ('unknown-erased', 'unknownOwnerPaths', 0), ('old-transfer', 'priorSource0061TestsTransferred', True), ('union', 'coverageExecUnion', True), ('formal', 'formalUpdated', True), ('accepted', 'newAccepted', 1), ('effort', 'effortPercent', 50), ('bool-method-count', 'uniqueProductMethodDelta', True), ('NoCode-erased', 'metadataClasses', {}), ('old-SQL-history', 'jointQualificationReplacedUnitHistory', old['jointQualificationReplacedUnitHistory']), ('old-Reader-correction', 'postDisclosureCorrections', {}), ('JS-erased', 'javascriptResourceDomain', {}), ('resource-erased', 'resourceOnlyReferences', []), ('owners', 'ownerStatusCounts', {}), ('cases-erased', 'cases', old['cases']), ('Source-removed', 'fullSourceUnits', old['fullSourceUnits']), ('source-count', 'sourceProgramDelta', 5), ('new-test-count', 'newTestIds', 27)]
    labels = []
    for label, field, value in vectors:
        bad = copy.deepcopy(current)
        bad[field] = value
        try:
            contract(bad)
        except ValueError:
            labels.append(label)
        else:
            raise ValueError('false joint metadata accepted: ' + label)
    for field, value in [('ordinaryCaseReferences', 2091), ('ordinaryWithoutCurrentCaseReference', 0), ('existingQualityFixtureCases', 0), ('phaseCompletionPercent', 100)]:
        bad = copy.deepcopy(current)
        bad['currentOrdinaryTestDeclarationReference'][field] = value
        try:
            contract(bad)
        except ValueError:
            labels.append('declaration-' + field)
        else:
            raise ValueError('false ordinary domain accepted')
    require(len(labels) == 34, 'all fixed finite negative vectors')
    require(current['owners']==old['owners'] and len(history)==1 and all(n.startswith('src/') for n in current['owners']),'no quality tool promoted into source owner/cost inventory')
    boundary_checks=[]
    for label,change in [
        ('quality-as-source-owner',lambda v:v['owners'].update({quality_path:dict(canonicalOwner='WBS-F03',canonicalCostOwner='WBS-F03')})),
        ('source-owner-count-inflation',lambda v:v['ownerStatusCounts'].update(UNKNOWN=303)),
        ('quality-reference-erased',lambda v:v.update(additionalScopeReferences=old['additionalScopeReferences'])),
        ('quality-as-ordinary',lambda v:v['currentOrdinaryTestDeclarationReference'].update(ordinaryCaseReferences=2808)),
        ('quality-hash-corrupt',lambda v:v['additionalScopeReferences'][-1].update(qualityToolSha256='0'*64))]:
        bad=copy.deepcopy(current);change(bad);require(bad!=current,'nondegenerate boundary '+label)
        try:contract(bad)
        except ValueError:boundary_checks.append(label)
        else:raise ValueError('quality namespace/cost domain accepted '+label)
    summary_keys = list(prior['summary'])
    for field in ('necessaryJointRepeatedMethods', 'totalRepeatedOriginalMethods'):
        if field not in summary_keys:
            summary_keys.append(field)
    for value in (old, prior, p, proof, current):
        verify(value['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation, registryManifestSha256=PIN, summary={k: current[k] for k in summary_keys}, qualityBoundaryNegativeVectors=len(boundary_checks),qualityBoundaryNegativeLabels=boundary_checks,metadataNegativeVectors=len(labels), negativeLabels=labels, allOldCasesAndUnrelatedProofsPreserved=True, singleExecSourceReplacements=1,newSourcePrograms=0,necessaryRepeatMethods=3,previousSourceProofsNotReplaced=False,previousProofsPreservedInHistory=True, originalMethodsReexecutedByRegistry=0, coverageExecUnion=False, currentOrdinaryTestDeclarationReference=decl, protocolMainSourceCount=158, protocolNormalMainSourceInventoryMatched=True, newAccepted=0, formalUpdated=False, wholeF03Accepted=False, whole451Accepted=False, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
