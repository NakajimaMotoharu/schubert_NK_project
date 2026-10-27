"""Reauthenticate22 nonempty reasons against eight unchanged source files; never load target Java."""
import copy
import json
import subprocess
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11570_batch_four_repository_source_review import evidence,match
from pg11569_four_repository_scope_facts import span

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11600-remaining-main-source-reauth-v3'
POST=data.BASE/'PG11602-remaining-main-source-reauth-post-v3'
PRIMARY_SHA=None
FILES={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthContextCodec.java',
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/cleanup/LogCleanupService.java',
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/InspectorEnvironmentFiles.java',
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java',
 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageStopHold.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/EncryptedSessionRequestCache.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/EncryptedSessionSecurityContextRepository.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SpringWebSession.java'}
IDS={f'PMD-{n:05d}' for n in (392,2729,2732,2733,2734,2737,2738,2739,2742,2743,2744,2747,2748,2749,2836,3342,3343,6161,6163,7430,7431,7452)}
HELPERS={f'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/cleanup/{n}.java' for n in ('CleanupStoppedException','CleanupStopReason','MaintenanceMutationGuard')}|{'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRepositoryException.java'}

def review():
    normal,original,old,later=evidence();rows=[];origins=Counter()
    assert normal['source']==SOURCE
    for path in FILES|HELPERS:
        current=(data.ROOT/path).read_bytes()
        assert data.sha(current)==normal['begin']['inputHashes'][path]
        if path in HELPERS:
            for historical in ('8c869d7cea21d587b859b3e72e3516d9d2deb5c8','aed19c6dca368e9717309d6f744d7917c6b7b32c'):
                assert subprocess.check_output(['git','show',historical+':'+path],cwd=data.ROOT)==current
    from pg11604_current_remaining_main_reason_delta import state
    current,refs,pending=state();assert IDS<=current and not IDS&refs and not IDS&pending
    selected=[r for r in original if r['id'] in IDS];assert len(selected)==22
    for raw in selected:
        assert raw['path'] in FILES
        folder,prior=match(raw,old,later)
        historical='8c869d7cea21d587b859b3e72e3516d9d2deb5c8' if folder=='PG6048' else 'aed19c6dca368e9717309d6f744d7917c6b7b32c'
        assert subprocess.check_output(['git','show',historical+':'+raw['path']],cwd=data.ROOT)==(data.ROOT/raw['path']).read_bytes()
        assert prior['status'] in ('REQUIRED_CONTRACT','CONTEXT_NOT_APPLICABLE') and prior['rawWarningRetained'] and prior.get('reason')
        assert raw['inputSha256']==normal['begin']['inputHashes'][raw['path']]
        _,_,fragment=span((data.ROOT/raw['path']).read_text(),raw['attributes']);origins[folder]+=1
        rows.append(dict(id=raw['id'],path=raw['path'],source=SOURCE,sourceSha256=raw['inputSha256'],attributes=raw['attributes'],originalRowSha256=raw['rowSha256'],currentSpanSha256=data.sha(fragment.encode()),diagnosticTextSha256=data.sha(raw['message'].encode()),disposition=prior['status'],
            historicalSource=historical,historicalManifest='PG6048-current-jdbc24-v2/manifest.json' if folder=='PG6048' else 'PG6354-batch-database-static-review-v1/manifest.json',historicalFindingId=prior['findingId'],historicalReasonRowSha256=data.sha(json.dumps(prior,sort_keys=True).encode()),
            reason=prior['reason'],reasonOrigin=folder,historicalReasonWasBlank=False,currentSourceFacts=None,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',rawWarningRetained=True,ptExecutionExempt=False,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None))
    assert origins==Counter(PG6048=19,PG6354=3)
    assert Counter(r['disposition'] for r in rows)==Counter(REQUIRED_CONTRACT=20,CONTEXT_NOT_APPLICABLE=2)
    designs={}
    for path,marker in [('documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md','SSC063'),('documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md','7.2.6'),('documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md','7.3'),('documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','SSC095/PG312')]:
        content=subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT);assert marker.encode() in content;designs[path]=data.sha(content)
    return dict(source=SOURCE,rows=rows,counts=dict(REQUIRED_CONTRACT=20,CONTEXT_NOT_APPLICABLE=2),historicalRecordOrigins=dict(origins),historicalReasonOrigins=dict(origins),reauthenticatedHistoricalReasons=22,newIndividualDispositions=0,currentSourceReviewFacts=0,
        mainSourceHashes={p:normal['begin']['inputHashes'][p] for p in sorted(FILES|HELPERS)},approvedDesigns=designs,originMainCommit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),
        preservedPriorFailure=dict(tool='tools/quality/pg11600_remaining_main_source_reauth.py',sha256='4b294e3d4907b8e60df93e6d63dcf3fd016e4f78017bb74d5071c77540ea4bf0',actualExit=1,outCreated=False,bug='BUG-1925',ykt='YKT-1674'),
        sourceCodeChanged=False,historicalRuntimeImportedAsCurrent=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0)

def require(value,expected):
    if value!=expected:raise ValueError('22 supported nonempty unchanged source reasons only; no old runtime reassignment')

def main():
    invocation=capture(__file__);assert not OUT.exists();value=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),reviewed=22,reauthenticatedHistoricalReasons=22,newIndividualDispositions=0,sourceCodeChanged=False,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,historicalRuntimeImportedAsCurrent=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation=capture(__file__);assert not POST.exists();primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA);value=data.read_checked(OUT/'review.json',primary['reviewSha256']);expected=review();require(value,expected)
    bads=[]
    for key,v in [('source','old'),('reauthenticatedHistoricalReasons',0),('newIndividualDispositions',22),('sourceCodeChanged',True),('historicalRuntimeImportedAsCurrent',True),('productTestsExecuted',22),('coverage',100),('rawWarningsRemoved',22),('wholeF03Accepted',True)]:
        bad=copy.deepcopy(value);bad[key]=v;bads.append(bad)
    for key,v in [('reason',''),('sourceSha256','0'*64),('disposition','PASS'),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(value);bad['rows'][0][key]=v;bads.append(bad)
    bad=copy.deepcopy(value);bad['rows'].pop();bads.append(bad)
    for bad in bads:
        try:require(bad,expected)
        except ValueError:pass
        else:raise AssertionError('incomplete/reasonless/runtime credit accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,metadataNegativeVectors=len(bads),reviewed=22,reauthenticatedHistoricalReasons=22,newIndividualDispositions=0,
        sourceCodeChanged=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,historicalRuntimeImportedAsCurrent=False,externalActions=0));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':main()
