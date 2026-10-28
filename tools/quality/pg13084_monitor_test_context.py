"""Eleven original real Test corrections and twenty retained worker contexts, not global F03 PASS."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13044_reference_identity_context import state_after as previous_state

SOURCE = '42ae92a74d57a9e1d031613d5b558af3ebe2925c'
OUT = data.BASE/'PG13084-monitor-test-context-v1'
POST = data.BASE/'PG13085-monitor-test-context-post-v1'
REMOVED = set('PMD-04704 PMD-04707 PMD-04812 PMD-04815 PMD-04834 PMD-04890 PMD-04893 PMD-04903 PMD-04906 PMD-04917 PMD-04907'.split())

def original():
    m = data.read_checked(data.BASE/'PG13070-monitor-test-originals-v1/manifest.json','faa795bf1bc06a56b4a926f48fdda20b60e7b8da7d0672439e0ab479628c598f')
    return data.read_checked(data.BASE/'PG13070-monitor-test-originals-v1/originals.json',m['originalsSha256'])

def state_after():
    ids,refs,pending = previous_state(); retained = {r['id'] for r in original()['originalFindings'] if r['rule'] == 'DoNotUseThreads'}
    assert REMOVED <= ids-refs and len(retained) == 20 and retained <= refs and not retained & pending
    return ids-REMOVED,refs,pending|retained

def signature(attributes):
    return {key:value for key,value in attributes.items() if key not in ['beginline','endline','begincolumn','endcolumn']}

def expected():
    s = data.read_checked(data.BASE/'PG13080-monitor-test-static-v1/manifest.json','8dd2ba543269195d0e4479ea48e8a55cfb846acac98c3d413dc3b56729ad8732')
    p = data.read_checked(data.BASE/'PG13082-monitor-test-post-v1/manifest.json','911c0f6768b0672873c942d4d2a9e7e89c92c18f4a16d39ee9b4515ed4a44fcc')
    plan = data.read_checked(data.BASE/'PG13074-monitor-test-plan-v1/manifest.json','26c3c4fd22d61e6bd8dc26ddbf4c47baee7b98c3963352123a0fac1d80f88a09')
    assert s['source'] == p['source'] == plan['source'] == SOURCE and s['actualExit'] == 1 and p['actualExit'] == 0
    assert p['observedTestExecutions'] == 81 and p['newTestIds'] == 0 and p['suites'] == 10 and p['rawStatic'] == 20
    assert p['spotbugsSixExit'] == 0 and p['staticGateExit'] == 1 and p['allMainClassesUnchanged'] == 1843
    assert p['changedTestPhysical'] == 11 and p['oldTestPhysicalUnchanged'] == 1961 and p['newTestPhysical'] == 0
    assert p['unexecutedClockAndObserveNowConfirmed'] and all(value['coverage100'] for value in p['monitorGroups'].values()) and len(p['monitorGroups']) == 10
    prior = original(); assert {r['id'] for r in prior['originalFindings'] if r['rule'] != 'DoNotUseThreads'} == REMOVED
    path = data.BASE/'PG13080-monitor-test-static-v1/pmd.xml'
    assert data.sha(path.read_bytes()) == s['reports']['pmd']['sha256']
    rows = []
    for file in ET.parse(path).getroot():
        if file.tag.rpartition('}')[2] != 'file': continue
        source = str(Path(file.get('name')).relative_to(data.ROOT))
        raw = (data.ROOT/source).read_bytes(); assert data.sha(raw) == s['sourceHashes'][source] == plan['wholeTestSourceHashes'][source]
        old = sorted([r for r in prior['originalFindings'] if r['path'] == source and r['rule'] == 'DoNotUseThreads'],key=lambda r:(r['line'],int(r['attributes']['begincolumn'])))
        current = sorted(list(file),key=lambda n:(int(n.get('beginline')),int(n.get('begincolumn'))))
        assert len(old) == len(current) == 2
        for before,now in zip(old,current):
            assert signature(before['attributes']) == signature(dict(now.attrib)) and before['message'] == now.text.strip()
            rows.append(dict(id=before['id'],path=source,source=SOURCE,sha256=data.sha(raw),rule=now.get('rule'),attributes=dict(now.attrib),
                canonicalOwner='WBS-P018-09',canonicalCostOwner='WBS-P018-09',
                classification='FINITE_SELF_OWNED_TEST_WORKER_RAW_RETAINED_PENDING_WHOLE_F03',actualViolation=None,
                reason='Existing own8worker/64task original oracle case, not a production container Thread; TWR and dedicated JVM240 preserved',
                limitation='Original invokeAll/pool close has no local timeout; one observed successful terminal is not a general termination guarantee. Outer owned JVM deadline is retained.',
                actualAllocatedPp=None,additionalSharedCostPp=0,originalSourceSha256=before['inputSha256']))
    assert len(rows) == len({r['id'] for r in rows}) == 20
    ids,refs,pending = state_after(); assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8461,3259,961,5202]
    return dict(source=SOURCE,rows=rows,sourceDerivedRaw=8461,mainRaw=1504,testRaw=6957,totalPriorCorrections=964,
        removedFindingIds=sorted(REMOVED),globalBaselineCorrectionsAdded=11,mainCorrections=0,testCorrections=11,
        existingSourceRebindings=20,newContextClassifications=0,joinedContextWarnings=3259,sourceReboundCurrentWholePending=961,
        noCurrentReferenceInThisJoin=5202,rawScope=20,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,
        monitorGroups=p['monitorGroups'],allTenMonitorGroupsCoverage100=True,selectedMainClosureCoverage100=p['selectedMainCoverage100'],
        observedTests=81,newTestIds=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,oldExecUnion=False)

def require(value,reference): assert value == reference

def main():
    invocation = capture(__file__); assert not OUT.exists(); value = expected(); verify(invocation); OUT.mkdir()
    data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        sourceDerivedRaw=8461,totalPriorCorrections=964,rawScope=20,removedFindingIds=sorted(REMOVED),joinedContextWarnings=3259,
        sourceReboundCurrentWholePending=961,actualViolationCount=None,newAccepted=0,wholeF03Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation = capture(__file__); assert not POST.exists()
    m = __import__('json').loads((OUT/'manifest.json').read_bytes()); value = data.read_checked(OUT/'review.json',m['reviewSha256']); reference = expected(); require(value,reference)
    labels = []
    for key,bad_value in [('source','0'*40),('sourceDerivedRaw',8472),('totalPriorCorrections',953),('mainCorrections',11),('testCorrections',0),('rawScope',0),('actualViolationCount',0),('newAccepted',1),('wholeF03Accepted',True)]:
        bad = copy.deepcopy(value); assert bad[key] != bad_value; bad[key] = bad_value
        try: require(bad,reference)
        except AssertionError: labels.append(key)
        else: raise AssertionError('wrong correction/rebinding/source qualification accepted')
    verify(invocation); POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=len(labels),nonVacuousLabels=labels,sourceDerivedRaw=8461,totalPriorCorrections=964,
        existingSourceRebindings=20,actualViolationCount=None,newAccepted=0,wholeF03Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
