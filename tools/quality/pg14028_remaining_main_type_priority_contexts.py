"""Seventeen retained raw JMS type-priority references; public source/XML metadata only."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE=cfg.SOURCE
OUT=data.BASE/'PG14028-remaining-main-type-priority-twenty-two-contexts-v1'
MEASURED=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
RULE='AvoidInstanceofChecksInCatchClause'
TARGETS=json.loads("{\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness.java\":[\"a9510db3be2c058715da8c4f089d3f49b2e9224447bf6685aeb23f12400d594e\",\"WBS-P018-05\",[\"PMD-00107\",\"PMD-00114\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/ApiMessagingRuntime.java\":[\"b67514d342a8f3be8891bb30c003731a98a6dc484814f873dcdb8a85414f60ed\",\"WBS-P005-03\",[\"PMD-00181\",\"PMD-00182\",\"PMD-00183\",\"PMD-00184\",\"PMD-00188\",\"PMD-00189\",\"PMD-00194\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/storage/ScenarioFileWriter.java\":[\"00beb3cfaba4dcb08f2991e03f898556e2fc8e320679deb1d61e98b90b30522b\",\"WBS-P008-03\",[\"PMD-00395\"]],\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/CleanupBackupAdmission.java\":[\"c8688816049150012c537335fd6db146c105857c85edb83bbf85d8a6dc85b383\",\"WBS-P017-06\",[\"PMD-02819\"]],\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/ConfigurationGroupResolver.java\":[\"101b894dd376757d29940596454e9a126e0783fc520acf88472ac66552118a45\",\"WBS-P018-01\",[\"PMD-03066\",\"PMD-03067\",\"PMD-03068\",\"PMD-03069\",\"PMD-03070\",\"PMD-03071\",\"PMD-03072\",\"PMD-03073\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness.java\":[\"bf5f3f6357c91a01dc2d8dfcf8b45687e42a011099d6c286cd54c3a6c8de35ab\",\"WBS-P018-06\",[\"PMD-07193\",\"PMD-07200\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java\":[\"134a6f35746447e6e27020ae8b82da5d67c136f0d20c46e94b41e5b8b81bc47f\",\"WBS-P005-02\",[\"PMD-07336\"]]}")
DESIGN={
 'documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md':'2fbf317dcc6d2048abb3c8ecdc9747e7b3d46cdba4753bec6bbc9e3ace5d5d1c',
 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md':'3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82',
 'documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md':'b721e6f7d0ee3f17cfe1a2d38512623814b0a10c8a7ad8ae737c62eeda192195',
 'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md':'d8be70ce4c170df7939f7803723bb021c99ba40a72819f9b5d861731425332b2',
 'documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md':'d861735e91a6930bbf239937deda29f3675fbf50817953a61e07c0255387fa66',
}
IDS={v for _,_,ids in TARGETS.values() for v in ids}

def reason(path,method):
    name=path.rpartition('/')[2]
    if name in ('ApiDependencyReadiness.java','WebDependencyReadiness.java'):
        return 'SSC330 readiness: owned DB/JMS close occurs before fixed catalog. With no primary propagate closing; direct cleanup Error overrides only non-Error primary, otherwise retain primary identity and transient secondary for module classification. DB failure cannot proceed to JMS. Graph9 actual execution remains HOLD; this source reference proves no live admission, resource cleanup or alternative completion.'
    if name=='ApiMessagingRuntime.java':
        return 'SSC314/334: startup notification Error overrides non-Error failure, but existing direct startup Error remains; runtime close exposes direct Error or wrapper with first-group cause. Classify retained/notification/cleanup only after owned group attempts. Reverse close skips confirmed phases, selects first direct Error and marks closed only after success. UNKNOWN nonreturn and actual consumers/graph/close remain unqualified.'
    if name=='ScenarioFileWriter.java':
        return 'SS333 collision classification belongs to the outer attempt failure catch, after nested deletePart catch ends. Retry only unpublished StorageIoException COLLISION, after directory/reservation scopes close; cleanup uncertainty retains capacity and fails fixed. Published ready is not deleted. The typed test is required before reason access, not live file/rename/resource proof.'
    if name=='CleanupBackupAdmission.java':
        return 'SS341/343 borrowed cleanup observation: known Repository cleanup becomes fixed IOException only if primary is not unknown. Unknown primary retains identity with newly fixed secondary, and unknown cleanup identity is not redacted. Failed rollback never authorizes autoCommit restoration. This is public code review, not investigation/recovery of a failed cohort or permission to mutate a database.'
    if name=='ConfigurationGroupResolver.java':
        return 'SSC063/PG174: checked IO/Interrupted primary yields to unknown Runtime/Error cleanup; Interrupted is reasserted. Unknown primary retains identity with fixed IOException secondary. Owned release/TERM-before-join must complete before buffer wipe/result return. Static type discrimination does not run getent, process, executor, TERM, private configuration or native owner actions.'
    assert name=='ArtemisReplyConsumers.java' and method=='start'
    return 'SSC333: outer startup catch retains direct primary Error after owned runtime close; separate close Error is considered only if primary was non-Error. Raw secondary identity/self-suppression guard precedes graph fallback. This instanceof is in the enclosing startup catch after nested cleanup catch, not its lexical predecessor. Actual callback/rollback/close/native graph remains unqualified.'

GUARDS={
 'ApiDependencyReadiness.java':['connection.close();','context.close();','if (primary == null || closing instanceof Error && !(primary instanceof Error))','TemporaryInfrastructureException.attachSecondary(primary, closing);','TemporaryInfrastructureException.preserveFatal(failure);'],
 'WebDependencyReadiness.java':['connection.close();','context.close();','if (primary == null || closing instanceof Error && !(primary instanceof Error))','WebStartupException.attachSecondary(primary, closing);','WebStartupException.preserveFatal(failure);'],
 'ApiMessagingRuntime.java':['notification instanceof Error && !(failure instanceof Error)','closing instanceof Error ? closing : Objects.requireNonNull(closing.getCause())','cleanup instanceof Error fatal && !(retained instanceof Error)','if (retained instanceof Error fatal) throw fatal;','groupClosed[index] = true;','failure == null || closing instanceof Error && !(failure instanceof Error)','TemporaryInfrastructureException.preserveFatal(failure);'],
 'ScenarioFileWriter.java':['if (state.created && !state.published)','directory.deletePart(id);','reservation.retain();','if (!state.published','failure instanceof StorageIoException storage','storage.reason() == StorageIoException.Reason.COLLISION','result = Optional.empty();'],
 'CleanupBackupAdmission.java':['if (unknown(primary))','primary.addSuppressed(new BatchRepositoryException());','if (cleanup instanceof BatchRepositoryException) throw unavailable();','borrowed.rollback();','borrowed.setAutoCommit(true);'],
 'ConfigurationGroupResolver.java':['primary instanceof IOException || primary instanceof InterruptedException','&& !(cleanup instanceof IOException)','if (primary instanceof InterruptedException) Thread.currentThread().interrupt();','primary.addSuppressed(unavailable());','throw primary;','release.close();'],
 'ArtemisReplyConsumers.java':['runtime.close();','if (failure != closing) failure.addSuppressed(closing);','if (failure instanceof Error fatal) throw fatal;','if (closingFailure instanceof Error fatal) throw fatal;','WebStartupException.preserveFatal(failure);','if (closingFailure != null) WebStartupException.preserveFatal(closingFailure);'],
}
def source_guards(path,text):
    for phrase in GUARDS[path.rpartition('/')[2]]:assert phrase in text
    if path.endswith('ConfigurationGroupResolver.java'):
        body=text[text.index('  private static void scope('):text.index('  private static void terminate(')]
        assert body.index('work.run();')<body.index('release.close();')<body.index('throw cleanup;')<body.index('primary.addSuppressed(unavailable());')
    if path.endswith('ArtemisReplyConsumers.java'):
        assert text.index('runtime.close();')<text.index('if (failure instanceof Error fatal)')<text.index('if (closingFailure instanceof Error fatal)')
    if path.endswith('ScenarioFileWriter.java'):
        assert text.index('directory.deletePart(id);')<text.index('failure instanceof StorageIoException storage')<text.index('result = Optional.empty();')

def catch_anchor(path,text,start):
    # These two conditions are after a nested catch has ended. A lexical rfind alone is wrong.
    if path.endswith('ScenarioFileWriter.java'):
        anchor=text.index('catch (StorageIoException | RuntimeException failure)')
    elif path.endswith('ArtemisReplyConsumers.java'):
        anchor=text.index('catch (RuntimeException | Error failure)')
    else:anchor=text.rfind('catch (',0,start)
    assert 0<=anchor<start
    return anchor

def wire(value):return json.dumps(value,sort_keys=True,separators=(',',':'))

def rows():
    normal,_=cfg.normal();hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    for p,pin in DESIGN.items():assert data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT))==data.sha((data.ROOT/p).read_bytes())==pin
    measured=data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1])
    assert measured['actualExit']==0 and measured['analysisComplete'] and not measured['processingErrors']
    facts=data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result=[]
    for path,(pin,owner,identities) in TARGETS.items():
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==hashes[path]==pin;source_guards(path,text)
        ownership=canonical(path,logical);assert ownership['canonicalOwner']==ownership['canonicalCostOwner']==owner
        selected=[r for r in facts if r['path']==path and r['rule']==RULE]
        prior=[r for r in original if r['id'] in identities]
        assert len(selected)==len(prior)==len(identities) and Counter(wire(r['attributes']) for r in selected)==Counter(wire(r['attributes']) for r in prior)
        seen=Counter()
        for row in sorted(prior,key=lambda r:r['id']):
            attributes=row['attributes'];key=wire(attributes);matches=[v for v in selected if v['attributes']==attributes]
            assert all(v['sourceSha256']==pin for v in matches) and row['inputSha256']==pin
            start,end,value=span(text,attributes);assert value in ('Error','IOException','InterruptedException','BatchRepositoryException','StorageIoException')
            anchor=catch_anchor(path,text,start)
            result.append(dict(id=row['id'],path=path,source=SOURCE,sourceSha256=pin,rule=RULE,attributes=attributes,originalRowSha256=row['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),typeToken=value,catchAnchor=anchor,occurrenceOrdinal=seen[key],rawDiagnosticMultiplicity=len(matches),reason=reason(path,attributes['method']),disposition='TYPE_PRIORITY_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership))
            seen[key]+=1
        assert all(seen[k]==len([v for v in selected if wire(v['attributes'])==k]) for k in seen)
    assert len(result)==22 and {r['id'] for r in result}==IDS
    assert len({(r['path'],r['spanStart'],r['spanEndExclusive']) for r in result})==15
    assert len({(r['path'],r['catchAnchor']) for r in result})==11
    return sorted(result,key=lambda r:r['id'])

if __name__=='__main__':
    invocation=capture(__file__);assert not OUT.exists();result=rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,approvedDesignHashes=DESIGN,nestedCatchScopeExplicitlyMapped=True))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=22,uniqueOperandSpans=15,uniqueCatchClauses=11,rawRetained=22,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
