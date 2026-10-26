"""Source-only local policy review of fifteen Main comment-only catch sites. Never execute retained owners."""
from collections import Counter
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10928-main-empty-catch-policy-v1'
POLICIES = {
    'PMD-00204':'FATAL_ROLLBACK_HALT_NO_ACK',
    'PMD-00231':'FATAL_ROLLBACK_HALT_NO_ACK',
    'PMD-00261':'FATAL_ROLLBACK_HALT_NO_ACK',
    'PMD-07342':'FATAL_ROLLBACK_HALT_NO_ACK',
    'PMD-02820':'ATTEMPTED_PURGE_FAILURE_STATE',
    'PMD-02821':'HEALTH_FAILURE_STATE',
    'PMD-02890':'COMPLETION_DIAGNOSIS_PRESERVES_UNKNOWN',
    'PMD-02893':'CADDY_BOUNDED_NOT_READY',
    'PMD-02906':'SERVICE_BOUNDED_NOT_LISTENING',
    'PMD-03133':'VANISHED_FD_NOT_OWNED_EVIDENCE',
    'PMD-03141':'VANISHED_FD_NOT_OWNED_EVIDENCE',
    'PMD-06133':'UNKNOWN_DIAGNOSIS_NOT_RELEASE',
    'PMD-06138':'UNKNOWN_FALLBACK_NOT_RELEASE',
    'PMD-06144':'INTERRUPTED_TICK_NOT_RELEASE',
    'PMD-07274':'WEB_UNKNOWN_DIAGNOSIS_NOT_RELEASE',
}
DESIGNS = [
    'documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md',
    'documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md',
    'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md',
    'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md',
    'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md',
]


def catch_header(text,line):
    suffix = ''.join(text.splitlines(keepends=True)[line-1:])
    values = canonical(suffix)
    index = values.index('catch')
    assert index <= 1 and values[index+1] == '('
    end = values.index(')',index+2)
    assert values[end+1:end+3] == ['{','}']
    return values[index+2:end]


def policy_facts(policy,text,line):
    before = '\n'.join(text.splitlines()[max(0,line-35):line-1])
    after = '\n'.join(text.splitlines()[line-1:line+35])
    if policy == 'FATAL_ROLLBACK_HALT_NO_ACK':
        assert 'rollbackAttempted.compareAndSet(false, true)' in before
        assert 'halted.set(true);' in before and 'onFatal.run();' in after
        assert '.rollback();' in before
        if 'ArtemisReplyConsumers' in text:
            assert 'if (selectedFatal != null) throw selectedFatal;' in after
        return 'Halted before one rollback attempt; catch cannot ACK or enable retry. API notify/return vs Web finally rethrows selected same Error per SSC332.'
    if policy in ('ATTEMPTED_PURGE_FAILURE_STATE','HEALTH_FAILURE_STATE'):
        assert 'boolean purgeSucceeded = false;' in text and 'boolean healthy = false;' in text
        assert '@Nullable Long after = null;' in text and 'purgeSucceeded = true;' in text
        assert 'BatchStepResult.Status.WARNING' in text and 'BatchStepResult.Status.FAILED' in text
        assert 'health.inspect(opsSession).get("nk.expiry")' in text
        assert '!= ArtemisQueuePressureClient.Pressure.CRITICAL' in text
        return 'Typed actual failure leaves its flag false/after absent; following healthy/purge status mapping distinguishes WARNING/FAILED. Native health also checks expiry critical; no actual health observed.'
    if policy == 'COMPLETION_DIAGNOSIS_PRESERVES_UNKNOWN':
        assert 'void failure(Throwable failure)' in before
        assert 'failure instanceof IOException ? "IO" : failure instanceof Error ? "FATAL" : "RUNTIME"' in before
        return 'SSC326 best-effort fixed classification cannot prevent return to original UNKNOWN-retaining owner; no normal release is established.'
    if policy == 'CADDY_BOUNDED_NOT_READY':
        assert 'budget.remainingNanos() > caddyRemainingFloor' in before and 'if (proxy.ready())' in before
        assert 'pause();' in after and 'stopOnly(' in after
        return 'Only successful ready breaks bounded loop; uncertainty pauses under existing parent budget and outer failure cleanup, never promotes readiness.'
    if policy == 'SERVICE_BOUNDED_NOT_LISTENING':
        assert 'childBudget.requireWithin();' in before and 'budget.requireWithin();' in before
        assert 'boolean ready = false;' in before and 'if (ready)' in after
        return 'ConnectException leaves ready false; parent/Unit budgets and prior-owner checks still gate the next iteration, not a success receipt.'
    if policy == 'VANISHED_FD_NOT_OWNED_EVIDENCE':
        assert 'Files.readSymbolicLink(entry)' in before and 'descriptors.add(' in before
        assert 'descriptors.contains(fields[9])' in text and 'return Set.copyOf(owned);' in text
        return 'Only NoSuchFileException racing FD closure is skipped; no descriptor is fabricated, listener membership still requires descriptor inclusion.'
    if policy.startswith('UNKNOWN_') or policy == 'INTERRUPTED_TICK_NOT_RELEASE':
        assert 'while (true) observeUnknownInterval(' in text
        assert 'while (true)' in text and 'retainUnknownRelease' in text
        if policy == 'UNKNOWN_DIAGNOSIS_NOT_RELEASE':
            assert 'System.err.println("service resource release unconfirmed")' in before
        elif policy == 'UNKNOWN_FALLBACK_NOT_RELEASE':
            assert 'fallback.run();' in before
        else:
            assert 'Thread.sleep(OBSERVATION_MILLIS)' in before
        return 'SSC318 finite diagnosis/tick is not owner exit. Failure or interruption cannot unwind the outer nonreturning UNKNOWN owner; actual execution remains HOLD.'
    assert policy == 'WEB_UNKNOWN_DIAGNOSIS_NOT_RELEASE'
    assert 'System.err.println("WEB cleanup unconfirmed")' in before
    assert 'while (true)' in text and 'Reference.reachabilityFence(unconfirmed);' in text
    return 'Fixed public diagnosis failure cannot release the borrowed frame; outer retention/fences remain. No native liveness/cleanup observation.'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected = [r for r in original if r['sourceKind'] == 'MAIN' and r['rule'] == 'EmptyCatchBlock']
    assert len(selected) == 15 and {r['id'] for r in selected} == set(POLICIES)
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE
    hashes = normal['begin']['inputHashes']
    designs = {p:subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT) for p in DESIGNS}
    assert 'API通知後return/Web同一Error再throw'.encode() in designs[DESIGNS[0]]
    assert 'ExpiryがCritical未満'.encode() in designs[DESIGNS[1]]
    assert 'SSC326'.encode() in designs[DESIGNS[3]] and 'SSC318'.encode() in designs[DESIGNS[3]]
    result = []
    for row in selected:
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == hashes[row['path']] == row['inputSha256']
        line = int(row['attributes']['beginline'])
        header = catch_header(text,line)
        assert len(header) >= 2
        policy = POLICIES[row['id']]
        reason = policy_facts(policy,text,line)
        result.append(dict(id=row['id'],reviewId='REV-F03-EMPTY-'+row['id'].split('-')[1],source=SOURCE,
            path=row['path'],sourceSha256=hashes[row['path']],rule=row['rule'],attributes=row['attributes'],
            originalRowSha256=row['rowSha256'],catchHeaderTokens=header,catchBodyTokens=[],policy=policy,reason=reason,
            reviewStatus='STATIC_LOCAL_FAILURE_POLICY_REVIEW_COMPLETE',technicalDisposition='NECESSARY_LOCAL_POLICY_CONTEXT',
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',currentWholeCaseRefs=[],productTestsExecuted=0,
            coverage=None,ptExecutionExempt=False,rawWarningRetained=True,scopeGeneralized=False,oldRuntimeReassigned=False))
    assert len({r['path'] for r in result}) == 10
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',result)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),reviewedMainFindings=15,reviewedMainSources=10,
        policyCounts=dict(Counter(r['policy'] for r in result)),approvedDesignHashes={p:data.sha(v) for p,v in designs.items()},
        approvedDesignBranch='origin/main',sourceDerivedRaw=9248,referencedRows=2711,currentWholePending=31,noCurrentReference=6537,
        rawWarningsRemoved=0,newMainOrTestChanges=0,productTestsExecuted=0,coverage=None,ptExecutionExempt=False,
        wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
