"""Fifteen manually reviewed finally necessities; raw warnings and graph/runtime HOLD retained."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13760-main-finally-fifteen-contexts-v1'
NORMAL = ('PG13596-lgs-remaining-two-branches-v1','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
TARGETS = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness.java':('a9510db3be2c058715da8c4f089d3f49b2e9224447bf6685aeb23f12400d594e','WBS-P018-05',{'PMD-00104':('verify','connection','primary'),'PMD-00111':('probe','context','primary')}),
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/CleanupRepository.java':('33f742d39f4b2bd3bc12c5dbd4f7099c44ce4447b9d9ce81adcaf00f1504bfc1','WBS-P017-07',{'PMD-03264':('execute','row','rowFailure'),'PMD-03269':('execute','statement','statementFailure'),'PMD-03274':('readLogProgress','row','rowFailure'),'PMD-03279':('readLogProgress','statement','statementFailure')}),
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java':('8d04ab28261de2e41ccc24790d732922f02c823aad5c0f374d6040e99cbe9a7e','WBS-P017-11',{'PMD-03348':('read','rows','rowFailure'),'PMD-03353':('read','statement','statementFailure')}),
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness.java':('bf5f3f6357c91a01dc2d8dfcf8b45687e42a011099d6c286cd54c3a6c8de35ab','WBS-P018-06',{'PMD-07190':('verify','connection','primary'),'PMD-07197':('verify','context','primary')}),
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java':('134a6f35746447e6e27020ae8b82da5d67c136f0d20c46e94b41e5b8b81bc47f','WBS-P005-02',{'PMD-07345':('deliveryFailure','selectedFatal','selectedFatal')}),
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/receipt/ReceiptReferenceRepository.java':('91ca27ecb2aea560cd08b26c0ef605b2bbbac756afb673722eef816a1ddfb2c4','WBS-P011-04',{'PMD-07389':('register','statement','statementFailure'),'PMD-07394':('read','row','rowFailure'),'PMD-07399':('read','statement','statementFailure'),'PMD-07408':('transaction','connection','connectionFailure')})}
DEPENDENCIES = {'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/JdbcResourceFailures.java':'f4cff9bb43cacfde5be699fd61d4e25526523d5ef5e478aa88dcbb8bdde6928a'}
REASONS = {
 'PMD-00104':'Owned JDBC probe connection closes before broker probe. A standalone close failure prevents admission; direct close Error supersedes non-Error primary, otherwise recorded primary remains through the existing transient graph helper. Removing the conditional throw can turn unsuccessful cleanup into readiness.',
 'PMD-00111':'Owned per-topology JMS context closes before admission. Its direct close Error must not be hidden behind ordinary probe failure; primary Error stays primary. Legacy/three-topology selection is unchanged. This reason does not requalify the held graph classifier or real provider cleanup.',
 'PMD-03264':'Cleanup execute result-row close is attempted once even before a pending return completes. Existing SQL/unknown replacement helper selects a close failure only when required; otherwise original primary stays. Statement remains outer owner, borrowed Connection remains parent-owned.',
 'PMD-03269':'Cleanup execute statement closes after row and before returned chunk escapes. No-primary/known-SQL plus unknown-close must throw selected close rather than report successful uncommitted chunk. Helper keeps the fixed Batch secondary instead of raw provider details.',
 'PMD-03274':'Log progress result-row close participates in the same SQL/unknown precedence as execute. A valid row is not a successful observation until close returns; primary identity and the outer statement owner remain unchanged.',
 'PMD-03279':'Log progress statement finally runs after nested row close. Conditional selected failure prevents pending result return; no commit/rollback/new Connection or change to the parent transaction is introduced.',
 'PMD-03348':'Expiry read null-guards rows then directly closes that same acquired object once. SSC310 requires selected SQL/unknown close precedence before Optional empty/present can return, including earlier guarded exits. It does not authorize cleanup, retry or broker mutation.',
 'PMD-03353':'Expiry read statement closes after nullable result scope and before observation return. Same SSC310 primary/secondary selection preserves unknown identity; direct finally is deliberate, not unconditional masking of body failure.',
 'PMD-07190':'Web DB probe connection must close before reply-queue admission. A selected direct close Error cannot be hidden by ordinary primary; other primary keeps its existing graph attachment policy. No graph or actual connection result is certified by this review.',
 'PMD-07197':'Web probe JMS context closes after transient consumer. Conditional close throw retains direct fatal precedence and prevents successful HTTP admission on cleanup failure; other primary remains unchanged. Management/native gates remain separate.',
 'PMD-07345':'SSC332 requires already selected Error identity to escape Web reply after onFatal notification, even if that callback throws. Finally rethrows only nonnull selectedFatal; when absent the callback result/failure remains untouched. Rollback is attempted before notification; no owned cleanup is skipped by this finally itself.',
 'PMD-07389':'Receipt register statement closes before same-PK readback within the owned transaction. Conditional SQL/unknown selection prevents a successful insert result escaping a failed close; transaction rollback/connection finally still apply.',
 'PMD-07394':'Receipt read row closes before statement and pending Optional result. Existing replace checks known-SQL graphs before discard, preserves primary unknown with new fixed diagnostic, and only selected close can override. Graph implementation itself remains held/unqualified.',
 'PMD-07399':'Receipt read statement closes after row; selected close failure cannot be ignored at return. The borrowed parameter connection belongs to outer transaction, not this method, and is not closed here.',
 'PMD-07408':'Receipt transaction closes its acquired connection after commit or rollback/failed configuration. Even a pending successful commit return requires close to return. A close failure is not proof commit failed and is not permission to issue new business work; unknown is retained for caller handling.'}
IDS = set(REASONS)

def source_guards(path,text,identity,part,resource,primary):
    assert part.startswith('finally {') and 'return ' not in part
    if identity == 'PMD-07345':
        assert 'if (selectedFatal != null) throw selectedFatal;' in part
        assert 'onFatal.run();\n    } finally {' in text and 'context.rollback();' in text
    elif identity in {'PMD-00104','PMD-00111','PMD-07190','PMD-07197'}:
        assert resource+'.close();' in part and 'if (primary == null || closing instanceof Error && !(primary instanceof Error)) {' in part
        assert 'throw closing;' in part and '.attachSecondary(primary, closing);' in part
        assert 'primary = failure;\n        throw failure;' in text
    else:
        assert resource+'.close();' in part and 'replace('+primary+', secondary)) throw secondary;' in part
        assert primary+' = failure;' in text
        if path.endswith('/CleanupRepository.java'):assert 'connection.close(' not in text and 'connection.commit(' not in text and 'connection.rollback(' not in text
        if path.endswith('/ExpiryAuditRepository.java'):assert 'if ('+resource+' != null)' in part

def rows():
    normal = data.read_checked(data.BASE/NORMAL[0]/'manifest.json',NORMAL[1]);assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    for p,pin in DEPENDENCIES.items():assert data.sha((data.ROOT/p).read_bytes()) == hashes[p] == pin
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result = []
    for path,(pin,owner,scopes) in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == pin
        ownership = canonical(path,logical);assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        selected = [r for r in facts if r['path'] == path and r['rule'] == 'DoNotThrowExceptionInFinally'];assert len(selected) == len(scopes)
        for identity,(method,resource,primary) in scopes.items():
            old, = [v for v in original if v['id'] == identity]
            r, = [v for v in selected if v['attributes'] == old['attributes']]
            assert old['path'] == path and old['rule'] == r['rule'] and old['inputSha256'] == r['sourceSha256'] == pin and r['attributes']['method'] == method
            start,end,part = span(text,r['attributes']);source_guards(path,text,identity,part,resource,primary)
            result.append(dict(id=identity,path=path,source=SOURCE,sourceSha256=pin,rule=r['rule'],method=method,resource=resource,primaryVariable=primary,attributes=r['attributes'],originalRowSha256=old['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(part.encode()),reason=REASONS[identity],disposition='FINALLY_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,graphAlgorithmQualified=False,nativeRuntimeProven=False,**ownership))
    assert len(result) == 15 and {r['id'] for r in result} == IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();result = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,dependencySourceHashes=DEPENDENCIES))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=15,rawRetained=15,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,graphAlgorithmQualified=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
