"""Independent one-source replacement and explicit quality-fixture case accounting."""
import copy
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg15994_current2094_reference_value_registry import SOURCE, PREV, PREV_POST, POST, INDEPENDENT, NAME, read, require, wire

PIN = '7eaf3d75b2eadf3ab0d38f642333aefff3bb56fd81acd5b31d16d55d02d58a17'
OUT = data.BASE / 'PG15996-current2094-reference-value-registry-post-v1'

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    old, prior, p, q, current = [read(v) for v in (PREV, PREV_POST, POST, INDEPENDENT, ('PG15994-current2094-reference-value-registry-v1', PIN))]
    require(all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (old, prior, p, q, current)) and prior['registryManifestSha256'] == PREV[1] and q['postSha256'] == POST[1] and q['semanticNegativeVectors'] == 23 and q['independentOracleNegativeVectors'] == 5, 'all same-source qualified truth-table references')
    local = []
    for filename, digest in p['xmlHashes'].items():
        raw = (data.BASE / POST[0] / filename).read_bytes()
        require(data.sha(raw) == digest, 'genuine XML hash')
        root = ET.fromstring(raw)
        require(all(int(root.get(k)) == 0 for k in ('failures', 'errors', 'skipped')), 'all fixture methods PASS')
        for c in root.findall('testcase'):
            require(not list(c), 'not skipped or failed')
            local.append((c.get('classname'), c.get('name')))
    old_cases = {(r['classname'], r['name']) for r in old['cases']}
    require(len(local) == len(set(local)) == 3 and not set(local) & old_cases, 'exact three new quality fixture cases')
    expected = copy.deepcopy(old)
    previous = copy.deepcopy(old['fullSourceUnits'][NAME])
    require(previous['physical'] == [NAME] and previous['four100'] is False and NAME not in expected['qualificationReplacedUnitHistory'], 'one old partial value Source')
    counters = p['executable'][NAME]['counters']
    require(p['fullSourceUnits'][NAME]['physical'] == [NAME] and counters == p['totals'] == p['fullSourceUnits'][NAME]['totals'] and all(type(c[k]) is int and c['missed'] == 0 and c['covered'] > 0 for c in counters.values() for k in ('missed', 'covered')), 'all same-exec positive four counters')
    for kind in counters:
        require(previous['counters'][kind]['covered'] + previous['counters'][kind]['missed'] == counters[kind]['covered'] + counters[kind]['missed'], 'same Source counter denominator')
    expected['qualificationReplacedUnitHistory'][NAME] = previous
    expected['fullSourceUnits'][NAME] = dict(post=POST[0], postSha256=POST[1], physical=[NAME], counters=copy.deepcopy(counters), four100=True, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=False)
    reference = dict(post=list(POST), independentPost=list(INDEPENDENT), source=SOURCE, fixture='tools/quality/architecture/RunReferencesTruthTableTest.java', fixtureSha256='57eb6860f5767a5e8c2967899f4cce13437e5c1a05fb19f4cbc313adcd628b57', tests=3, newUniqueMethods=3, necessaryRepeatedMethods=0, normalOrdinaryTestSourceDomain=False, wholeSourceReplaced=NAME, countedInOriginalExecs=True, coverageExecUnion=False)
    expected['valueFixtureQualificationReferences'] = [reference]
    expected['originalPostReferences'].append(dict(name=POST[0], sha256=POST[1], tests=3, suites=1, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope='NEW_INDEPENDENT_PRIMITIVE_BOOLEAN16_QUALITY_FIXTURE3_ONE_COMPLETE_SOURCE_NOT_NORMAL_TEST_DECLARATIONS'))
    cases = old_cases | set(local)
    units = expected['fullSourceUnits']
    four = {c for u in units.values() if u['four100'] for c in u['physical']}
    expected.update(invocation=current['invocation'], previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}), originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + 3, uniqueProductMethodDelta=3, newTestIds=3, sourceProgramDelta=0, four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - expected['metadataClasses'].keys()), incompleteSourcePrograms=sum(not (u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()))
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    inventory = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', inventory['files']['exact-ordinary-bindings.json'])
    keys = {(b['className'], b['method']) for b in bindings}
    require(len(cases & keys) == 2085 and len(cases - keys) == 9 and not set(local) & keys, 'ordinary declarations unchanged, fixture cases 6+3')
    decl.update(existingQualityFixtureCases=9)
    expected['currentOrdinaryTestDeclarationReference'] = decl
    def contract(value):
        require(wire(value) == wire(expected), 'all independently reconstructed single-source replacement/case/history domains')
    contract(current)
    vectors = [('tests-as-normal', 'tests', 2091), ('Source-added', 'sourceProgramDelta', 1), ('physical-added', 'measuredPhysical', 655), ('four-erased', 'four100SourcePrograms', 251), ('four-double', 'four100Physical', 367), ('four-code-erased', 'four100ExecutablePhysical', 354), ('pending-erased', 'incompleteSourcePrograms', 0), ('JVM-double', 'totalProductExecs', 125), ('method-double', 'totalMethodExecutions', 2229), ('repeated-invented', 'totalRepeatedOriginalMethods', 135), ('history-erased', 'qualificationReplacedUnitHistory', {}), ('joint-history-erased', 'jointQualificationReplacedUnitHistory', {}), ('joint-reference-erased', 'jointQualificationReferences', []), ('fixture-reference-erased', 'valueFixtureQualificationReferences', []), ('Catalog-proof-erased', 'additionalQualificationReferences', []), ('digest-correction-erased', 'postDisclosureCorrections', {}), ('resource-erased', 'resourceOnlyReferences', []), ('JS-erased', 'javascriptResourceDomain', {}), ('owners-erased', 'owners', {}), ('natural-double', 'naturalZeroBranchSourcePrograms', 177), ('NoCode-erased', 'metadataPhysical', 0), ('new-as-repeat', 'uniqueProductMethodDelta', 0), ('bool-count', 'newTestIds', True), ('old-source-transfer', 'priorSource0061TestsTransferred', True), ('union', 'coverageExecUnion', True), ('formal', 'formalUpdated', True), ('accepted', 'newAccepted', 1), ('effort', 'effortPercent', 100), ('cases-erased', 'cases', old['cases']), ('Source-erased', 'fullSourceUnits', old['fullSourceUnits'])]
    labels = []
    for label, key, value in vectors:
        bad = copy.deepcopy(current)
        bad[key] = value
        try:
            contract(bad)
        except ValueError:
            labels.append(label)
        else:
            raise ValueError('false value replacement accepted: ' + label)
    for field, value in [('ordinaryCaseReferences', 2088), ('existingQualityFixtureCases', 6), ('ordinaryWithoutCurrentCaseReference', 0), ('phaseCompletionPercent', 100)]:
        bad = copy.deepcopy(current)
        bad['currentOrdinaryTestDeclarationReference'][field] = value
        try:
            contract(bad)
        except ValueError:
            labels.append('ordinary-' + field)
        else:
            raise ValueError('quality fixture mixed into normal declarations')
    require(len(labels) == 34, 'finite34 metadata vectors')
    for value in (old, prior, p, q, current):
        verify(value['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation, registryManifestSha256=PIN,
        summary={k: current[k] for k in prior['summary']}, metadataNegativeVectors=len(labels), negativeLabels=labels,
        oneSourceReplacement=NAME, newSourcePrograms=0, originalMethodsReexecutedByRegistry=0,
        currentOrdinaryTestDeclarationReference=decl, protocolMainSourceCount=158, protocolNormalMainSourceInventoryMatched=True,
        newAccepted=0, formalUpdated=False, wholeF03Accepted=False, whole451Accepted=False, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
