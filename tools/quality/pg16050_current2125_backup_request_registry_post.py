"""Independent XML/counter addition, retaining all prior source/fixture/cost domains."""
from collections import Counter
import copy
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg16048_current2125_backup_request_registry import SOURCE, PREV, PREV_POST, POST, INDEPENDENT, NAME, SCOPE, read, require, wire

PIN = '1481270818c601b5881b4f6e9fe55a9d4ac18e17e8a3698bf683161affdb71a9'
OUT = data.BASE / 'PG16050-current2125-backup-request-registry-post-v1'


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    old, prior, p, q, current = [read(v) for v in (PREV, PREV_POST, POST, INDEPENDENT, ('PG16048-current2125-backup-request-registry-v1', PIN))]
    require(all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (old, prior, p, q, current)) and prior['registryManifestSha256'] == PREV[1] and q['postSha256'] == POST[1] and (q['semanticNegativeVectors'], q['independentOracleNegativeVectors']) == (24, 5), 'all genuine independently qualified current witnesses')
    local = []
    for filename, digest in p['xmlHashes'].items():
        raw = (data.BASE / POST[0] / filename).read_bytes()
        require(data.sha(raw) == digest, 'original XML digest')
        root = ET.fromstring(raw)
        require(all(int(root.get(k)) == 0 for k in ('failures', 'errors', 'skipped')), 'actual success XML only')
        for row in root.findall('testcase'):
            require(not list(row), 'no skipped/failed case')
            local.append((row.get('classname'), row.get('name')))
    old_cases = {(r['classname'], r['name']) for r in old['cases']}
    require(len(local) == len(set(local)) == 9 and len({c for c, n in local}) == 1 and not set(local) & old_cases, 'new exact9 methods/one suite')
    names = [NAME, NAME + '$Verification']
    require(p['completeSourceUnitClosure'] == {NAME: sorted(names)} and set(p['physicalClasses']) == set(names) and p['metadataClasses'] == [], 'complete actual Main Source closure')
    counters = {}
    for kind in ('LINE', 'METHOD', 'CLASS', 'BRANCH'):
        for name in names:
            row = p['executable'][name]['counters'][kind]
            require(all(type(value) is int and value >= 0 for value in row.values()), 'actual typed counters')
        counters[kind] = {field: sum(p['executable'][name]['counters'][kind][field] for name in names) for field in ('covered', 'missed')}
        require(counters[kind]['missed'] == 0 and counters[kind]['covered'] > 0, 'one-exec Source allfour complete')
    require(counters == p['totals'] == p['fullSourceUnits'][NAME]['totals'] and p['singleSession'] is True and p['crcMismatch'] == 0 and p['sessionIdentity'] and p['execSha256'], 'same counters and exact single exec/session')
    expected = copy.deepcopy(old)
    require(NAME not in expected['fullSourceUnits'], 'exact new Source, no superseding old proof')
    expected['fullSourceUnits'][NAME] = dict(post=POST[0], postSha256=POST[1], physical=sorted(names), counters=counters, four100=True, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=False)
    for path, row in p['owners'].items():
        require(path not in expected['owners'] or expected['owners'][path] == row, 'shared responsibility unchanged')
        expected['owners'][path] = copy.deepcopy(row)
    expected['originalPostReferences'].append(dict(name=POST[0], sha256=POST[1], tests=9, suites=1, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope=SCOPE))
    methods = old_cases | set(local)
    units = expected['fullSourceUnits']
    physical = {n for u in units.values() for n in u['physical']}
    four = {n for u in units.values() if u['four100'] for n in u['physical']}
    require(len(physical) == sum(len(u['physical']) for u in units.values()), 'disjoint all whole Source families')
    expected.update(invocation=current['invocation'], previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(methods)], suiteNames=sorted({c for c, n in methods}), tests=len(methods), suites=len({c for c, n in methods}), originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + len(local), uniqueProductMethodDelta=len(local), newTestIds=len(local), sourceProgramDelta=1, measuredSourcePrograms=len(units), measuredPhysical=len(physical), executablePhysical=len(physical - expected['metadataClasses'].keys()), four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - expected['metadataClasses'].keys()), ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in expected['owners'].values())), unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in expected['owners'].values()), lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    inventory = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', inventory['files']['exact-ordinary-bindings.json'])
    keys = {(r['className'], r['method']) for r in bindings}
    require(len(keys) == 5786 and set(local) <= keys and len(methods & keys) == 2116 and len(methods - keys) == 9, 'all new ordinary cases, separate existing9 quality fixtures')
    decl.update(ordinaryCaseReferences=len(methods & keys), ordinaryWithoutCurrentCaseReference=len(keys - methods))
    expected['currentOrdinaryTestDeclarationReference'] = decl

    def contract(value):
        require(wire(value) == wire(expected), 'all independently reconstructed raw/XML/counter and preserved old domains')

    contract(current)
    vectors = [('tests', 2116), ('suites', 283), ('sourceProgramDelta', 0), ('measuredSourcePrograms', 476), ('measuredPhysical', 660), ('executablePhysical', 621), ('four100SourcePrograms', 255), ('four100Physical', 372), ('four100ExecutablePhysical', 361), ('totalProductExecs', 126), ('totalMethodExecutions', 2248), ('totalRepeatedOriginalMethods', 148), ('uniqueProductMethodDelta', 0), ('newTestIds', True), ('incompleteSourcePrograms', 0), ('metadataPhysical', 0), ('naturalZeroBranchSourcePrograms', 177), ('fullSourceUnits', old['fullSourceUnits']), ('cases', old['cases']), ('owners', {}), ('qualificationReplacedUnitHistory', {}), ('jointQualificationReplacedUnitHistory', {}), ('jointQualificationReferences', []), ('valueFixtureQualificationReferences', []), ('postDisclosureCorrections', {}), ('coverageExecUnion', True), ('priorSource0061TestsTransferred', True), ('formalUpdated', True), ('newAccepted', 1), ('effortPercent', 100)]
    labels = []
    for key, value in vectors:
        bad = copy.deepcopy(current)
        bad[key] = value
        try:
            contract(bad)
        except ValueError:
            labels.append(key)
        else:
            raise ValueError('unrejected registry mutation: ' + key)
    for field, value in [('ordinaryCaseReferences', 2125), ('ordinaryWithoutCurrentCaseReference', 0), ('existingQualityFixtureCases', 0), ('phaseCompletionPercent', 100)]:
        bad = copy.deepcopy(current)
        bad['currentOrdinaryTestDeclarationReference'][field] = value
        try:
            contract(bad)
        except ValueError:
            labels.append('ordinary-' + field)
        else:
            raise ValueError('ordinary versus phase/fixture domain changed')
    require(len(labels) == 34, 'independent finite34 mutations')
    for value in (old, prior, p, q, current):
        verify(value['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation, registryManifestSha256=PIN,
        summary={k: current[k] for k in prior['summary']}, metadataNegativeVectors=len(labels), negativeLabels=labels,
        newSourcePrograms=1, newUniqueMethods=9, newIncompleteSources=0, newIncompletePhysical=0,
        incompletePhysicalClasses=91, newProductExecutions=1, allOldCasesAndSourceProofsPreserved=True,
        currentOrdinaryTestDeclarationReference=decl, protocolMainSourceCount=158, protocolNormalMainSourceInventoryMatched=True,
        originalMethodsReexecutedByRegistry=0, coverageExecUnion=False, actualBackupOrToolAuthorityVerified=False,
        newAccepted=0, formalUpdated=False, wholeF03Accepted=False, whole451Accepted=False, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
