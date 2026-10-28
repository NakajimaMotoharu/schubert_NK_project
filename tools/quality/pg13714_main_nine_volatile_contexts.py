"""Nine manually reviewed visibility contracts bound to exact current source, not runtime proof."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from public_java_digest_provenance import LEX
from trace_owner_join import canonical

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13714-main-nine-volatile-contexts-v1'
NORMAL = ('PG13596-lgs-remaining-two-branches-v1','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
BASE = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'
TARGETS = {
 BASE+'bootstrap/WebManagementServer.java':('f4b820069ae18d539f6ceb62fd2b2e3b95afe27dafb0bdaf72e35c1fe53a01cf','WBS-P018-06',{'started':('PMD-07226',6)}),
 BASE+'bootstrap/WebNativeRuntime.java':('c9701244fed7a903c0858a5b8ef4bd78a3ddd499b76bbb9358a5f7181c4bec45','WBS-P018-06',{'replies':('PMD-07249',5),'replay':('PMD-07250',4),'retry':('PMD-07251',4),'http':('PMD-07252',5),'management':('PMD-07253',5)}),
 BASE+'logging/WebLogReplayWorker.java':('51972e99e350715e5404d70a08af31f8a7be26b3b143919d79bfa4363c450ab8','WBS-P006-04',{'lastReport':('PMD-07303',3)}),
 BASE+'messaging/ArtemisReplyConsumers.java':('134a6f35746447e6e27020ae8b82da5d67c136f0d20c46e94b41e5b8b81bc47f','WBS-P005-02',{'stopping':('PMD-07329',4),'started':('PMD-07330',3)})}
REASONS = {
 'PMD-07226':'Successful server.start publishes started under stopLock; promote/ready read outside that lock. Volatile supplies visibility, not a compound atomic readiness snapshot or actual selector termination proof.',
 'PMD-07249':'Under ownerLock start captures replies before listener start; health reads one local reference and close retains ownership. Volatile publishes the acquired handle, not a fully started graph or native liveness.',
 'PMD-07250':'Under ownerLock start publishes the returned log worker; health and close each copy the reference. No compound update depends on volatile; actual worker termination remains a separate join condition.',
 'PMD-07251':'Under ownerLock start publishes the returned revocation worker; health/close each snapshot the reference. This is visibility only, never a permit or a native termination proof.',
 'PMD-07252':'Owned HTTP callback captures a partial owner before failure; health/close read a local snapshot. Volatile publishes that handle without claiming the entire startup graph is atomic or complete.',
 'PMD-07253':'Management bind is captured before start/promote; ready/close copy that reference. Volatile keeps lock-free observation visible, not actual socket, ready or cleanup completion.',
 'PMD-07303':'One worker replaces a nonnull immutable four-int Report; snapshot readers do not join. Volatile publishes the reference, not a shared epoch with the independent AtomicLong counters.',
 'PMD-07329':'Close sets stopping under stateLock before context.close; ready reads without stateLock and refuses stopping. This visible stop fence does not assert an unknown provider close completed.',
 'PMD-07330':'Start sets started after opened.start returns under stateLock; lock-free ready observes that publication alongside stopping and terminal. No compound read-modify-write or linearizable flag tuple is claimed.'}
IDS = set(REASONS)

def source_guards(path,text):
    if path.endswith('/WebNativeRuntime.java'):
        assert text.count('synchronized (ownerLock) {') == 2 and 'owned -> http = owned' in text
        assert all('var '+a+' = '+b+';' in text for a,b in [('reply','replies'),('log','replay'),('revoke','retry'),('web','http'),('control','management')])
    elif path.endswith('/WebManagementServer.java'):
        assert 'server.start();\n      started = true;' in text and 'return started && !stopping.get() && promoted.get() && healthy.getAsBoolean();' in text
        assert 'if (started) serverStopped = true;' in text and 'stopLock.lock();' in text
    elif path.endswith('/WebLogReplayWorker.java'):
        assert 'lastReport = Objects.requireNonNull(action.dispatch(), "web log report");' in text and 'return new Snapshot(completedCycles.get(), failedCycles.get(), lastReport);' in text
    else:
        assert 'opened.start();\n      started = true;' in text and 'return !stopping && started && !terminal.get();' in text
        assert 'stopping = true;\n      try {\n        context.close();' in text and 'stateLock.lock();' in text

def rows():
    normal = data.read_checked(data.BASE/NORMAL[0]/'manifest.json',NORMAL[1]);assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result = []
    for path,(pin,expected_owner,fields) in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == pin
        source_guards(path,text);owner = canonical(path,logical);assert owner['canonicalOwner'] == owner['canonicalCostOwner'] == expected_owner
        selected = [r for r in facts if r['path'] == path and r['rule'] == 'AvoidUsingVolatile'];assert len(selected) == len(fields)
        assert {r['sourceSha256'] for r in facts if r['path'] == path} == {pin}
        ts = [m for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        for row in selected:
            a = row['attributes'];field = a['variable'];identity,count = fields[field]
            old, = [r for r in original if r['id'] == identity]
            assert old['path'] == path and old['rule'] == row['rule'] and old['attributes'] == a and old['inputSha256'] == pin
            start,end,value = span(text,a);assert value == field
            occurrences = [m.start() for m in ts if m.group() == field];assert len(occurrences) == count and start in occurrences
            result.append(dict(id=identity,path=path,source=SOURCE,sourceSha256=pin,rule=row['rule'],field=field,attributes=a,originalRowSha256=old['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),fieldTokenOffsets=occurrences,fieldTokenCount=count,reason=REASONS[identity],disposition='CONTRACT_REQUIRED_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,compoundAtomicityProven=False,nativeRuntimeProven=False,productTestsExecuted=0,**owner))
    assert len(result) == 9 and {r['id'] for r in result} == IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();value = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=value))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=9,rawRetained=9,productTestsExecuted=0,sourceChanged=False,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
