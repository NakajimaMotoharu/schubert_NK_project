"""Forty-six source-only compound cleanup reasons; retain raw and all dynamic HOLDs."""
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE = '1be156b6ebb139713db31a561b8b024972975471'
OUT = data.BASE/'PG12432-resource-compound-context-v1'
RESOURCE = 'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'
PROCESS = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScope.java'
PRECEDENCE = 'primaryinstanceofIOException&&!(secondaryinstanceofIOException)'
QUERY_PRECEDENCE = 'primaryinstanceofIOException||primaryinstanceofInterruptedException||primaryinstanceofStopGateException'
SANITIZED = 'primary.addSuppressed(newStorageIoException(StorageIoException.Reason.UNAVAILABLE));'
QUERY_SANITIZED = 'primary.addSuppressed(newStopGateException(StopGateFailure.COMMAND_FAILURE));'
IO_REASON = 'failureinstanceofStorageIoExceptionstorage&&failure.getSuppressed().length==0?storage.reason():StorageIoException.Reason.UNAVAILABLE'
INTERRUPT = 'if(primaryinstanceofInterruptedException)Thread.currentThread().interrupt();'
CONTROLS = {
    ('ResourceScope','acquire'):['Objects.requireNonNull(acquire,"resource acquire")','Objects.requireNonNull(release,"resource release")','Objects.requireNonNull(action,"resource action")','Rresource=acquire.open()','owned=Objects.requireNonNull(resource,"acquired resource")','result=action.run(owned)','if(resource!=null)','release.close(resource)',PRECEDENCE,'throwsecondary;',SANITIZED,'throwprimary;','release.close(owned);returnresult;',IO_REASON],
    ('ResourceScope','use'):['Objects.requireNonNull(release,"resource release")','Objects.requireNonNull(action,"resource action")','result=action.run();','release.close();',PRECEDENCE,'throwsecondary;',SANITIZED,'throwprimary;','release.close();returnresult;',IO_REASON],
    ('ProcessResourceScope','acquire'):['Objects.requireNonNull(acquire,"query acquire")','Objects.requireNonNull(release,"query release")','Objects.requireNonNull(work,"query work")','Rresource=acquire.open()','owned=Objects.requireNonNull(resource,"acquired query resource")','work.run(owned)','if(resource!=null)','release.accept(resource)',QUERY_PRECEDENCE,'!(cleanupinstanceofStopGateException)',INTERRUPT,'throwcleanup;',QUERY_SANITIZED,'throwprimary;','release.accept(owned);'],
    ('ProcessResourceScope','use'):['work.run();','release.run();',QUERY_PRECEDENCE,'!(cleanupinstanceofStopGateException)',INTERRUPT,'throwcleanup;',QUERY_SANITIZED,'throwprimary;']}

def catches(ts,point):
    found = []
    for i in range(len(ts)-1):
        if [t for t,_ in ts[i:i+2]] != ['catch','(']:
            continue
        depth = 1;j = i+2
        while depth:
            depth += (ts[j][0] == '(')-(ts[j][0] == ')');j += 1
        header_end = j-1
        assert ts[j][0] == '{'
        depth = 1;k = j+1
        while depth:
            depth += (ts[k][0] == '{')-(ts[k][0] == '}');k += 1
        if i <= point < k:
            found.append((i,header_end,k-1))
    assert found
    return min(found,key=lambda r:r[2]-r[0])

def main():
    invocation = capture(__file__);assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    inputs = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in inputs.items())
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected = [r for r in original if r['path'] in (RESOURCE,PROCESS) and r['rule'] in ('AvoidCatchingGenericException','AvoidInstanceofChecksInCatchClause')]
    assert len(selected) == len({r['id'] for r in selected}) == 46
    support = ['src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java','src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/StopGateException.java','src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/StopGateFailure.java']
    closure = {p:inputs[p] for p in [RESOURCE,PROCESS,*support]}
    authority_path = 'documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md'
    authority_commit = '8b91944df5820535e23ba2469740f1c0aa94c447'
    authority = subprocess.check_output(['git','show',authority_commit+':'+authority_path],cwd=data.ROOT)
    assert 'bodyが既知IOExceptionでcloseが未知Runtime/Errorならcloseの元unknownを優先する' in authority.decode() and 'InterruptedException' in authority.decode()
    rows = []
    for row in selected:
        path = row['path'];text = (data.ROOT/path).read_text();assert row['inputSha256'] == inputs[path] == data.sha(text.encode())
        a = row['attributes'];lines = text.splitlines(keepends=True)
        start = sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        end = sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts = [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        point = next(i for i,(_,offset) in enumerate(ts) if offset == start)
        lo,hi,method = min((r for r in functions(ts) if r[0] <= point <= r[1]),key=lambda r:r[1]-r[0])
        assert method == a['method'];controls = CONTROLS[(Path(path).stem,method)]
        body = ''.join(t for t,_ in ts[lo:hi+1]);assert all(c in body for c in controls)
        ca,ce,cb = catches(ts,point);header = [t for t,_ in ts[ca:ce+1]]
        if row['rule'] == 'AvoidCatchingGenericException':
            assert ts[point][0] in ('RuntimeException','Error') and point <= ce
            kind = 'RETHROW_UNCHECKED_COMPOUND_CLEANUP_BOUNDARY'
            reason = 'Caller-supplied release/action may fail with unchecked RuntimeException or Error as well as declared IO/query failures. The owner must attempt exactly the acquired resource release, preserve the selected original failure identity and release-before-result rule, rather than skip cleanup or normalize unchecked/fatal failures as success. SS333 explicitly requires both primary and secondary unknown classification; narrowing/removing the catch loses the compound boundary.'
        elif Path(path).stem == 'ResourceScope' and header[-2] == 'failure':
            kind = 'DECLARED_IO_REASON_ONLY_NORMALIZATION'
            reason = 'Only the outer declared IOException is converted to the existing path-free StorageIoException reason. An existing StorageIoException retains its reason only without compound suppressed failure; other IO or compound IO becomes UNAVAILABLE. The runtime subtype check preserves approved reason semantics; unchecked Runtime/Error never enters this outer IO normalizer.'
        else:
            kind = 'EXPLICIT_KNOWN_UNKNOWN_FAILURE_PRECEDENCE'
            reason = 'Type checks implement the approved known IO/query/StopGate versus unknown Runtime/Error priority, not instanceof-based dispatch of business objects. Unknown cleanup dominates a known primary, otherwise original primary is rethrown with fixed sanitized secondary; query interrupted primary restores the interrupt flag before unknown cleanup escapes. Catch splitting or Java TWR substitution would change this explicit precedence and same-object/self-suppression behavior.'
        rows.append(dict(id=row['id'],path=path,rule=row['rule'],attributes=a,originalRowSha256=row['rowSha256'],source=SOURCE,sourceSha256=inputs[path],sourceSpanSha256=data.sha(text[start:end].encode()),method=method,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),catchHeader=header,catchTokenSha256=data.sha('\0'.join(t for t,_ in ts[ca:cb+1]).encode()),controls=controls,kind=kind,reason=reason,disposition='CONTEXT_NOT_APPLICABLE',currentWholeJoinPending=True,productTestsExecutedByReview=0,dynamicPtStatus='NOT_EXECUTED',oldRuntimeReassigned=False,newAccepted=0))
    count = len({r['id'] for r in rows})
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256='f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3',reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=count,rawRetained=count,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=None,originalTwoSourceRaw=48,unselectedThreadRaw=2,closureSourceHashes=closure,upperAuthority=dict(path=authority_path,commit=authority_commit,sha256=data.sha(authority)),sourceCodeChanged=False,staticAnalyzerReissued=False,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED',coverage=None,newAccepted=0,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
