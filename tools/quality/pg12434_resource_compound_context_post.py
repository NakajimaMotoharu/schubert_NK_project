"""Independent source/catch/method/authority checks for46 retained cleanup contexts; no Product calls."""
import copy
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg12248_main_local_maps_post import enclosing_method

SOURCE = '1be156b6ebb139713db31a561b8b024972975471'
PIN = '20cd6d45c1b336ce6f5320a2844e7ca4bd455a8103beb179bb7e19bd252035de'
OUT = data.BASE/'PG12434-resource-compound-context-post-v1'
PATHS = {'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java':18,'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScope.java':28}
REQUIRED = {
    ('ResourceScope','acquire'):['if(resource!=null)','release.close(resource)','release.close(owned);returnresult;','primaryinstanceofIOException&&!(secondaryinstanceofIOException)','primary.addSuppressed(newStorageIoException(StorageIoException.Reason.UNAVAILABLE));','throwprimary;','throwsecondary;','failureinstanceofStorageIoExceptionstorage&&failure.getSuppressed().length==0?storage.reason():StorageIoException.Reason.UNAVAILABLE'],
    ('ResourceScope','use'):['result=action.run();','release.close();returnresult;','primaryinstanceofIOException&&!(secondaryinstanceofIOException)','primary.addSuppressed(newStorageIoException(StorageIoException.Reason.UNAVAILABLE));','throwprimary;','throwsecondary;','failureinstanceofStorageIoExceptionstorage&&failure.getSuppressed().length==0?storage.reason():StorageIoException.Reason.UNAVAILABLE'],
    ('ProcessResourceScope','acquire'):['if(resource!=null)','work.run(owned)','release.accept(resource)','release.accept(owned);','primaryinstanceofIOException||primaryinstanceofInterruptedException||primaryinstanceofStopGateException','!(cleanupinstanceofStopGateException)','if(primaryinstanceofInterruptedException)Thread.currentThread().interrupt();','primary.addSuppressed(newStopGateException(StopGateFailure.COMMAND_FAILURE));','throwprimary;','throwcleanup;'],
    ('ProcessResourceScope','use'):['work.run();','release.run();','primaryinstanceofIOException||primaryinstanceofInterruptedException||primaryinstanceofStopGateException','!(cleanupinstanceofStopGateException)','if(primaryinstanceofInterruptedException)Thread.currentThread().interrupt();','primary.addSuppressed(newStopGateException(StopGateFailure.COMMAND_FAILURE));','throwprimary;','throwcleanup;']}

def catch_region(ts,point):
    stack = [];pairs = {}
    for i,(value,_) in enumerate(ts):
        if value == '{':
            stack.append(i)
        elif value == '}':
            assert stack;pairs[stack.pop()] = i
    assert not stack
    regions = []
    for i,(value,_) in enumerate(ts):
        if value != 'catch':
            continue
        assert ts[i+1][0] == '('
        end = next(j for j in range(i+2,len(ts)) if ts[j][0] == ')')
        assert ts[end+1][0] == '{'
        if i <= point <= pairs[end+1]:
            regions.append((i,end,pairs[end+1]))
    if not regions:
        raise ValueError('one enclosing catch region required')
    return sorted(regions,key=lambda r:r[2]-r[0])[0]

def main():
    invocation = capture(__file__);assert not OUT.exists()
    p = data.BASE/'PG12432-resource-compound-context-v1';m = data.read_checked(p/'manifest.json',PIN)
    rows = data.read_checked(p/'review.json',m['reviewSha256'])['rows']
    normal = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    originals = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected = {r['id']:r for r in originals if r['path'] in PATHS and r['rule'] in ('AvoidCatchingGenericException','AvoidInstanceofChecksInCatchClause')}
    assert len(selected) == len(rows) == len({r['id'] for r in rows}) == 46 and set(selected) == {r['id'] for r in rows}
    assert all(sum(r['path'] == path for r in rows) == count for path,count in PATHS.items())
    def validate(row):
        if row.get('id') not in selected:
            raise ValueError('known selected original ID required')
        original = selected[row['id']];path = original['path'];a = original['attributes'];method = a['method']
        text = (data.ROOT/path).read_text();sha = data.sha(text.encode());assert sha == normal['begin']['inputHashes'][path] == original['inputSha256']
        ts = [(n.group(),n.start()) for n in LEX.finditer(text) if not n.group().startswith(('//','/*'))]
        lines = text.splitlines(keepends=True);start = sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end = sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point = next(i for i,(_,offset) in enumerate(ts) if offset == start)
        lo,hi = enclosing_method(ts,method,point);body = ''.join(t for t,_ in ts[lo:hi+1])
        ca,ce,cb = catch_region(ts,point);header = [t for t,_ in ts[ca:ce+1]]
        if original['rule'] == 'AvoidCatchingGenericException':
            assert ts[point][0] in ('RuntimeException','Error') and point <= ce
            kind = 'RETHROW_UNCHECKED_COMPOUND_CLEANUP_BOUNDARY'
        elif Path(path).stem == 'ResourceScope' and header[-2] == 'failure':
            kind = 'DECLARED_IO_REASON_ONLY_NORMALIZATION'
        else:
            kind = 'EXPLICIT_KNOWN_UNKNOWN_FAILURE_PRECEDENCE'
        expected = dict(path=path,rule=original['rule'],attributes=a,originalRowSha256=original['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),method=method,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),catchHeader=header,catchTokenSha256=data.sha('\0'.join(t for t,_ in ts[ca:cb+1]).encode()),kind=kind,disposition='CONTEXT_NOT_APPLICABLE',currentWholeJoinPending=True,productTestsExecutedByReview=0,dynamicPtStatus='NOT_EXECUTED',oldRuntimeReassigned=False,newAccepted=0)
        controls = row.get('controls')
        if any(row.get(k) != v for k,v in expected.items()) or not row.get('reason') or not isinstance(controls,list) or not set(REQUIRED[(Path(path).stem,method)]) <= set(controls) or not all(c and c in body for c in controls):
            raise ValueError('exact method/catch/scope/control and no runtime credit required')
    for row in rows:
        validate(row)
    negatives = []
    for key,wrong in [('id','foreign'),('source','0'*40),('sourceSha256','0'*64),('sourceSpanSha256','0'*64),('method','other'),('methodTokenSha256','0'*64),('catchHeader',[]),('catchTokenSha256','0'*64),('controls',[]),('reason',''),('kind','NO_RULE'),('disposition','SUPPRESSED'),('currentWholeJoinPending',False),('dynamicPtStatus','PASS'),('productTestsExecutedByReview',1),('oldRuntimeReassigned',True),('newAccepted',1)]:
        bad = copy.deepcopy(rows[0]);assert bad[key] != wrong;bad[key] = wrong
        try:
            validate(bad)
        except ValueError:
            negatives.append(key)
        else:
            raise AssertionError('invalid source-only row accepted')
    def counts(value):
        expected = dict(sourceContexts=46,rawRetained=46,wholeStaticScopeRaw=None,originalTwoSourceRaw=48,unselectedThreadRaw=2,sourceCorrections=0,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED',newAccepted=0)
        if any(value.get(k) != v for k,v in expected.items()):
            raise ValueError('selected46 distinct from original48 and no runtime/whole credit required')
    counts(m)
    for key,wrong in [('sourceContexts',48),('rawRetained',3),('wholeStaticScopeRaw',0),('originalTwoSourceRaw',46),('sourceCorrections',46),('productTestsExecuted',1),('dynamicPtStatus','PASS'),('newAccepted',1)]:
        bad = dict(m);assert bad[key] != wrong;bad[key] = wrong
        try:
            counts(bad)
        except ValueError:
            negatives.append('manifest.'+key)
        else:
            raise AssertionError('invalid source-only cardinality accepted')
    authority = m['upperAuthority'];assert authority['commit'] == '8b91944df5820535e23ba2469740f1c0aa94c447'
    assert data.sha(subprocess.check_output(['git','show',authority['commit']+':'+authority['path']],cwd=data.ROOT)) == authority['sha256']
    assert len(m['closureSourceHashes']) == 5 and all(data.sha((data.ROOT/p).read_bytes()) == h == normal['begin']['inputHashes'][p] for p,h in m['closureSourceHashes'].items())
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=46,rawRetained=46,metadataNegativeVectors=len(negatives),metadataNegativeLabels=negatives,originalTwoSourceRaw=48,wholeStaticScopeRaw=None,upperAuthority=authority,closureSourceHashes=m['closureSourceHashes'],dynamicPtStatus='NOT_EXECUTED',productTestsExecuted=0,coverage=None,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
