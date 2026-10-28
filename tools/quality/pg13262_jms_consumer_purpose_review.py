"""Read-only three-owner source review of72 original diagnostics, never runtime/JMS qualification."""
from collections import Counter
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_diagnostic_v3 import signature
from pg13258_current_catalog_supplement import state_after as previous_state

OUT = data.BASE/'PG13262-jms-consumer-purpose-review-v1'
PREFIX = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'
SPECS = {
    'QuestionWorkConsumers':('WBS-P012-01',['PT-JMS-CORE-001..008'],['var result = new QuestionWorkConsumers(factory, onUnconfirmed);','var context = result.context;','result.close();','synchronized (lock)'],
        ['core007AllPartialOwnersSignalStopBeforeCloseAndPreserveNotificationFaults','core004EveryPartialContextStageClosesAndFatalPriorityIsPreserved']),
    'SyncRequestConsumers':('WBS-P005-03',['PT-JMS-013'],['new ArrayList<>(CONCURRENCY)','opened.add(context);','runtime.closeAfterFailure(retained);','if (contextClosed[index]) continue;','contextClosed[index] = true;','synchronized (closeLock)'],
        ['closeIsIdempotentAndAggregatesAllContextFailures','failedStartupPreservesClosingFailureAsSuppressed']),
    'WebLogConsumers':('WBS-P006-05',['PT-JMS-015'],['WebLogConsumers runtime = new WebLogConsumers(factory, onUnconfirmed);','JMSContext opened = runtime.context;','runtime.close();','synchronized (closeLock)'],
        ['closeIsIdempotentAndStartupPreservesCloseFailure','jmsown002AcquisitionFailureAndNullKeepIdentityWithoutFatalNotification']),
}
PURPOSE = {
    'CloseResource':('LONG_LIVED_OWNER_AND_CONTEXT_CHILD', 'Context is stored before provider configuration and handed back in the runtime; startup failure drains the owner, normal lifetime ends through close; consumer lifetime depends on JMSContext. TWR around start would terminate returned runtime.',
        'Provider child-close and pre/post handoff effects are not dynamically proved; close may block or fail; no automatic leak/false-positive conclusion.'),
    'AvoidCatchingGenericException':('BOUNDARY_FAILURE_RETENTION_NOT_SUCCESS', 'Catch RuntimeException/Error around listener, rollback, startup notification and close to halt delivery, attempt owner cleanup and preserve nonzero/fatal policy. Failed rollback catch does not acknowledge: fatal notification and process owner termination remain required.',
        'Callback failures, arbitrary Throwable graph access and external nonzero termination remain HOLD; this purpose review neither proves all graph branches nor normalizes an unknown close.'),
    'AvoidInstanceofChecksInCatchClause':('FATAL_PRIORITY_AND_IDENTITY', 'Runtime/Error branch chooses fatal precedence, avoids self-suppression and distinguishes direct Error from retryable delivery before notifying or rethrowing.',
        'All exceptional combinations and graph/accessor behavior require original dynamic tests; no branch coverage or identity success is inferred.'),
    'AvoidSynchronizedStatement':('SERIAL_OWNER_CLOSE_STATE', 'Dedicated close lock protects closed/contextClosed state and provider drain; halted is set before entering the lock and successful close is recorded only after provider return.',
        'Lock acquisition/provider close has no local deadline; callback concurrency, parent budget and all shutdown postconditions remain unproved by source review.'),
}

def key(row):return row['path'],signature(row['attributes'],row['message'])

def selected():
    ids,refs,pending = previous_state();assert [len(ids),len(refs),len(pending)] == [8022,3273,1183]
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    paths = {PREFIX+n+'.java' for n in SPECS};rows = [r for r in original if r['id'] in ids-refs and r['path'] in paths]
    assert len(rows) == 72 and Counter(Path(r['path']).stem for r in rows) == Counter({n:24 for n in SPECS})
    assert Counter(r['rule'] for r in rows) == Counter(CloseResource=7,AvoidCatchingGenericException=39,AvoidInstanceofChecksInCatchClause=23,AvoidSynchronizedStatement=3)
    return rows

def expected():
    rows = selected()
    m = data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/manifest.json','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
    actual = data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/findings.json',m['findingsSha256']);counts = Counter(key(r) for r in actual)
    n = data.read_checked(data.BASE/'PG13242-business-delivery-literal-v1/manifest.json','73d770b42807892d7b39bdc6d7da6d45e73857c152cb6aace83c0387e3239496')
    inventory = json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());files = {};tests = {};owners = {}
    for name,(owner,test_ids,anchors,methods) in SPECS.items():
        path = PREFIX+name+'.java';text = (data.ROOT/path).read_text();sha = data.sha(text.encode())
        assert sha == n['begin']['inputHashes'][path] and all(a in text for a in anchors)
        assert 'throw new IllegalStateException(' in text and '.halted.set(true);' in text and 'if (closed) return;' in text
        assert 'onUnconfirmed.accept(' in text and 'closed = true;' in text and 'onFatal.run();' in text and 'notification != failure' in text
        registered = [r for r in inventory['currentPhysicalCandidate']['artifacts'] if r['path'] == path];assert len(registered) == 1
        assert registered[0]['owner'] == registered[0]['costOwner'] == owner;owners[path] = dict(canonicalOwner=owner,canonicalCostOwner=owner)
        files[path] = dict(sha256=sha,sourceLines=len(text.splitlines()),anchors=anchors,wholeSourceReadForReview=True,rdUiSsAndExistingTestIds=test_ids)
        test = path.replace('/main/','/test/').replace('.java','Test.java');raw = (data.ROOT/test).read_bytes();assert data.sha(raw) == n['begin']['inputHashes'][test]
        assert all(('void '+method+'(') in raw.decode() for method in methods)
        tests[test] = dict(sha256=data.sha(raw),witnessMethods=methods,observation='SOURCE_EXPECTATIONS_ONLY_NOT_EXECUTED',testIds=test_ids)
    result = []
    for r in rows:
        text = (data.ROOT/r['path']).read_text();assert data.sha(text.encode()) == r['inputSha256']
        matches = [a for a in actual if key(a) == key(r)];assert matches and counts[key(r)] >= sum(key(x) == key(r) for x in rows)
        classification,purpose,risk = PURPOSE[r['rule']];line = int(r['attributes']['beginline'])
        result.append(dict(id=r['id'],path=r['path'],sourceSha256=files[r['path']]['sha256'],rule=r['rule'],attributes=r['attributes'],message=r['message'],enclosingMethod=r['attributes']['method'],
            currentOccurrenceCount=len(matches),currentPositions=[a['attributes']['beginline'] for a in matches],individualOccurrenceIdentity='UNIQUE' if len(matches) == 1 else 'MULTISET_ONLY_NOT_GUESSED',
            sourceLine=text.splitlines()[line-1],classification=classification,purpose=purpose,residualRisk=risk,**owners[r['path']],manualPurposeReviewComplete=True,actualViolation=None,
            status='SOURCE_PURPOSE_REVIEWED_DYNAMIC_AND_WHOLE_STATIC_HOLD',ptExecutionExempt=False,measuredProductCounters=None,productTestsExecuted=0))
    return dict(source=m['source'],sourceFiles=files,testSourceExpectations=tests,rows=result,scopeCount=72,purposeReferencesBefore=3273,purposeReferencesAfter=3345,pendingAfter=1255,noReferenceAfter=4677,
        rawDiagnostics=8022,originalCorrections=1419,newCorrections=0,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,actualViolationCount=None,qualityGateExit=1,wholeF03Accepted=False,whole451Accepted=False)

def validate(value):assert json.dumps(value,sort_keys=True) == json.dumps(expected(),sort_keys=True)

def state_after():
    m = json.loads((OUT/'manifest.json').read_bytes());v = data.read_checked(OUT/'review.json',m['reviewSha256']);validate(v)
    ids,refs,pending = previous_state();new = {r['id'] for r in v['rows']};assert len(new) == 72 and new <= ids-refs
    return ids,refs|new,pending|new

def main():
    invocation = capture(__file__);assert not OUT.exists();value = expected();validate(value);verify(invocation);OUT.mkdir();data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,source=value['source'],reviewSha256=data.sha((OUT/'review.json').read_bytes()),newPurposeReferences=72,newCorrections=0,productTestsExecuted=0,newAccepted=0,
        sourceOrTestChanged=False,externalActions=0,qualityGateExit=1,coverage=None,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
