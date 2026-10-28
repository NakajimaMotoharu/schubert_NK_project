"""Read existing static type metadata and explicit source contexts, never execute Product code."""
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13038_throwable_identity_post import state_after as before_state

OUT = data.BASE/'PG13042-reference-identity-context-v1'
SOURCE = '2f4290e7e511ea30224d087f78d44964d3488919'
GROUPS = {
    'REQUEST_SCOPE_BINDING': ('PMD-00007 PMD-00014 PMD-00021 PMD-00036 PMD-00043',
        'Private Snapshot retains the original request reference and actor owner; reply requires the same request scope, not a reconstructed value-equivalent request'),
    'THREAD_OWNER_OR_SELF_JOIN': ('PMD-00093 PMD-00325 PMD-00382 PMD-06167 PMD-06169 PMD-07267 PMD-07307 PMD-07320 PMD-07427',
        'Compare current physical Thread with the captured owner/owned worker, preventing self-wait/join or cross-thread terminal/scope use'),
    'OPAQUE_ISSUER_AND_BASELINE': ('PMD-02800 PMD-02802 PMD-03021 PMD-03022 PMD-03023 PMD-03024 PMD-03025',
        'Private Intent/Baseline/TerminalReceipt retains its issuing gate and exact baseline; equal serialized fields cannot substitute another issuer/frame'),
    'EXACT_TERMINAL_RECEIPT_CONTINUITY': ('PMD-02868 PMD-03114 PMD-03117 PMD-03120',
        'Retain exactly the already observed child receipt across stop/recheck/handoff, not an equal-looking replacement or a new success receipt'),
    'LEXICAL_SCOPE_STACK': ('PMD-07322',
        'The current ThreadLocal must be this exact top Scope before pop restores previous; equivalent trace data is not the same stack frame'),
    'CURRENT_SESSION_REPOSITORY_INSTANCE': ('PMD-07429 PMD-07435',
        'The request SessionRepositoryFilter attribute must be the configured current repository instance before owned local invalidation/Logout; do not accept a different repository by value'),
}

def wanted_ids():
    ids = [item for names,_ in GROUPS.values() for item in names.split()]
    assert len(ids) == len(set(ids)) == 28
    return set(ids)

def state_after():
    ids,refs,pending = before_state(); chosen = wanted_ids()
    assert chosen <= ids-refs and not chosen & pending
    return ids,refs|chosen,pending|chosen

def collect():
    prior = data.read_checked(data.BASE/'PG13038-throwable-identity-post-v1/manifest.json','2db97b5ef8db4f2c84b69c3096a3ec966d89a42529db5c7c9c3bc9956b241f4d')
    prior_review = data.read_checked(data.BASE/'PG13038-throwable-identity-post-v1/review.json',prior['reviewSha256'])
    typed = data.read_checked(data.BASE/'PG13036-throwable-identity-types-v3/manifest.json',prior['typedManifestSha256'])
    assert prior['source'] == typed['source'] == SOURCE and prior['actualExit'] == typed['actualExit'] == 0
    rows = {row['id']:row for row in prior_review['typedNonThrowableUnclassified']}
    assert set(rows) == wanted_ids() and not set(rows)&set(prior_review['newlyReviewedContextIds'])
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in typed['begin']['sourceHashes'].items())
    result = []; supports = {}
    for category,(names,reason) in GROUPS.items():
        for identifier in names.split():
            row = copy.deepcopy(rows[identifier]); path = row['path']; text = (data.ROOT/path).read_text(); lines = text.splitlines(); line = row['originalLine']
            assert data.sha((data.ROOT/path).read_bytes()) == row['sourceSha256'] == typed['begin']['sourceHashes'][path]
            assert lines[line-1].strip() == row['sourceSnippet'] and row['leftThrowable'] == row['rightThrowable'] == 'NO'
            assert row['operator'] in ['EQUAL_TO','NOT_EQUAL_TO']
            if category == 'REQUEST_SCOPE_BINDING':
                assert 'saved.request == request' in row['sourceSnippet']
                assert 'private Snapshot(' in text and 'this.request = request;' in text and 'new Snapshot(' in text
            elif category == 'THREAD_OWNER_OR_SELF_JOIN':
                assert row['leftType'] == row['rightType'] == 'java.lang.Thread' and 'Thread.currentThread()' in row['sourceSnippet']
            elif category == 'OPAQUE_ISSUER_AND_BASELINE':
                assert ('owner' in row['sourceSnippet'] and 'this' in row['sourceSnippet']) or 'before.baseline != baseline' in row['sourceSnippet']
                assert 'private Intent(' in text or 'private Baseline(' in text
            elif category == 'EXACT_TERMINAL_RECEIPT_CONTINUITY':
                assert row['leftType'].endswith('.TerminalReceipt') and row['rightType'] == row['leftType']
                assert any(marker in row['sourceSnippet'] for marker in ['completedReceipt() != backupReceipt','receipt.stopped(baseline, held) != held','receipt.stopped(baseline, before) != before','actual != observedReceipt.get()'])
            elif category == 'LEXICAL_SCOPE_STACK':
                assert row['sourceSnippet'] == 'if (CURRENT.get() != this)' and all(s in text for s in ['previous = CURRENT.get();','CURRENT.set(this);','else CURRENT.set(previous);'])
            else:
                assert 'SESSION_REPOSITORY_ATTR) != sessions)' in row['sourceSnippet'] and 'this.sessions = Objects.requireNonNull(sessions,' in text
            supporting = [(i+1,s.strip()) for i,s in enumerate(lines) if any(marker in s for marker in ['private Snapshot(','this.request = request;','new Snapshot(','private Intent(','private Baseline(','private TerminalReceipt(','this.owner = owner;','owner = Thread.currentThread();','new Thread(this::run','observedReceipt.set(value);','return before;','previous = CURRENT.get();','CURRENT.set(this);','else CURRENT.set(previous);','this.sessions = Objects.requireNonNull(sessions,'])]
            supports[path] = dict(sourceSha256=row['sourceSha256'],supportingSourceLines=supporting)
            row.update(purposeCategory=category,reason=reason,sourceContext=[s.strip() for s in lines[max(0,line-3):line+4]],
                status='STATIC_DIAGNOSTIC_CONTEXT_REVIEWED_DYNAMIC_HOLD',manualPurposeReviewComplete=True,actualViolation=None,
                dynamicExecutionQualificationInferred=False,actualAllocatedPp=None,additionalSharedCostPp=0)
            result.append(row)
    ids,refs,pending = state_after(); assert [len(ids),len(refs),len(pending),len(ids-refs)] == [8472,3259,941,5213]
    return dict(source=SOURCE,reviewedRows=result,sourceSupports=supports,reviewedContextRows=28,sourceFiles=len(supports),
        newlyReviewedContextIds=sorted(rows),sourceCodeChanged=False,productTestsExecuted=0,productClassesLoaded=0,newProductClassFiles=0,
        sourceDerivedRaw=8472,totalPriorCorrections=953,globalRawCorrectionsAdded=0,joinedContextWarnings=3259,
        sourceReboundCurrentWholePending=941,noCurrentReferenceInThisJoin=5213,actualViolationCount=None,newAccepted=0,
        wholeF03Accepted=False,whole451Accepted=False,effortPercent=None,unknownDynamicCorrectness=True,
        limits='Static purpose only, not defect exemption or runtime ownership/receipt/session/termination proof; existing type analysis reused without replay')

def require(value,reference):
    assert value == reference and len(value['reviewedRows']) == 28 and value['newAccepted'] == 0
    assert value['productTestsExecuted'] == value['productClassesLoaded'] == value['newProductClassFiles'] == 0
    assert value['actualViolationCount'] is None and value['unknownDynamicCorrectness']

def main():
    invocation = capture(__file__); assert not OUT.exists(); reference = collect(); require(reference,reference); labels = []
    for key,bad_value in [('source','0'*40),('reviewedContextRows',56),('sourceDerivedRaw',8444),('actualViolationCount',0),('productTestsExecuted',28),('newAccepted',1),('wholeF03Accepted',True),('unknownDynamicCorrectness',False)]:
        bad = copy.deepcopy(reference); assert bad[key] != bad_value; bad[key] = bad_value
        try: require(bad,reference)
        except AssertionError: labels.append(key)
        else: raise AssertionError('misstated static-purpose result accepted')
    verify(invocation); OUT.mkdir(); data.write(OUT/'review.json',reference)
    data.write(OUT/'manifest.json',dict(source=SOURCE,actualExit=0,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        reviewedContextRows=28,sourceFiles=reference['sourceFiles'],metadataNegativeVectors=len(labels),nonVacuousLabels=labels,
        sourceDerivedRaw=8472,totalPriorCorrections=953,joinedContextWarnings=3259,sourceReboundCurrentWholePending=941,
        productTestsExecuted=0,productClassesLoaded=0,newProductClassFiles=0,newAccepted=0,actualViolationCount=None,
        wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
