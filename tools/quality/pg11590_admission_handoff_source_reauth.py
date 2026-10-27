"""Reauthenticate19 nonempty reasons against four unchanged source files; never load target Java."""
import copy
import json
import subprocess
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11570_batch_four_repository_source_review import evidence,match
from pg11569_four_repository_scope_facts import span

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11590-admission-handoff-source-reauth-v1'
POST=data.BASE/'PG11592-admission-handoff-source-reauth-post-v1'
PRIMARY_SHA=None
FILES={f'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/{n}.java' for n in ('SchemaHistoryAdmission','ServiceDatabaseAdmission')}|{f'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/cleanup/{n}.java' for n in ('InspectorLockHandoff','MaintenanceMutationGuard')}
IDS={f'PMD-{n:05d}' for n in (2717,2718,2719,2721,2722,2750,2751,6106,6107,6108,6111,6112,6113,6117,6118,6119,6122,6123,6124)}

def review():
    normal,original,old,later=evidence();rows=[];origins=Counter()
    assert normal['source']==SOURCE
    helper='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures.java'
    for path in FILES|{helper}:
        current=(data.ROOT/path).read_bytes()
        assert data.sha(current)==normal['begin']['inputHashes'][path]
        for historical in ('8c869d7cea21d587b859b3e72e3516d9d2deb5c8','aed19c6dca368e9717309d6f744d7917c6b7b32c'):
            assert subprocess.check_output(['git','show',historical+':'+path],cwd=data.ROOT)==current
    tokens=''.join(canonical((data.ROOT/helper).read_text()))
    assert 'if(primary==null||(primaryinstanceofSQLException&&!(secondaryinstanceofSQLException)))returntrue;' in tokens
    assert 'newSQLNonTransientConnectionException("database admission resource failure","08001")' in tokens
    selected=[r for r in original if r['id'] in IDS];assert len(selected)==19
    for raw in selected:
        assert raw['path'] in FILES
        folder,prior=match(raw,old,later)
        assert prior['status']=='REQUIRED_CONTRACT' and prior['rawWarningRetained'] and prior.get('reason')
        assert raw['inputSha256']==normal['begin']['inputHashes'][raw['path']]
        _,_,fragment=span((data.ROOT/raw['path']).read_text(),raw['attributes']);origins[folder]+=1
        rows.append(dict(id=raw['id'],path=raw['path'],source=SOURCE,sourceSha256=raw['inputSha256'],attributes=raw['attributes'],originalRowSha256=raw['rowSha256'],currentSpanSha256=data.sha(fragment.encode()),diagnosticTextSha256=data.sha(raw['message'].encode()),disposition='REQUIRED_CONTRACT',
            historicalManifest='PG6048-current-jdbc24-v2/manifest.json' if folder=='PG6048' else 'PG6354-batch-database-static-review-v1/manifest.json',historicalFindingId=prior['findingId'],historicalReasonRowSha256=data.sha(json.dumps(prior,sort_keys=True).encode()),
            reason=prior['reason'],reasonOrigin=folder,historicalReasonWasBlank=False,currentSourceFacts=None,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',rawWarningRetained=True,ptExecutionExempt=False,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None))
    assert origins==Counter(PG6048=12,PG6354=7)
    designs={}
    for path,marker in [('documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md','SSC063'),('documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md','7.3'),('documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','SSC095/PG312')]:
        content=subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT);assert marker.encode() in content;designs[path]=data.sha(content)
    return dict(source=SOURCE,rows=rows,counts=dict(REQUIRED_CONTRACT=19),historicalRecordOrigins=dict(origins),historicalReasonOrigins=dict(origins),reauthenticatedHistoricalReasons=19,newIndividualDispositions=0,currentSourceReviewFacts=0,
        mainSourceHashes={p:normal['begin']['inputHashes'][p] for p in sorted(FILES|{helper})},approvedDesigns=designs,originMainCommit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),
        sourceCodeChanged=False,historicalRuntimeImportedAsCurrent=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0)

def require(value,expected):
    if value!=expected:raise ValueError('19 supported nonempty unchanged source reasons only; no old runtime reassignment')

def main():
    invocation=capture(__file__);assert not OUT.exists();value=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),reviewed=19,reauthenticatedHistoricalReasons=19,newIndividualDispositions=0,sourceCodeChanged=False,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,historicalRuntimeImportedAsCurrent=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation=capture(__file__);assert not POST.exists();primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA);value=data.read_checked(OUT/'review.json',primary['reviewSha256']);expected=review();require(value,expected)
    bads=[]
    for key,v in [('source','old'),('reauthenticatedHistoricalReasons',0),('newIndividualDispositions',19),('sourceCodeChanged',True),('historicalRuntimeImportedAsCurrent',True),('productTestsExecuted',19),('coverage',100),('rawWarningsRemoved',19),('wholeF03Accepted',True)]:
        bad=copy.deepcopy(value);bad[key]=v;bads.append(bad)
    for key,v in [('reason',''),('sourceSha256','0'*64),('disposition','PASS'),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(value);bad['rows'][0][key]=v;bads.append(bad)
    bad=copy.deepcopy(value);bad['rows'].pop();bads.append(bad)
    for bad in bads:
        try:require(bad,expected)
        except ValueError:pass
        else:raise AssertionError('incomplete/reasonless/runtime credit accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,metadataNegativeVectors=len(bads),reviewed=19,reauthenticatedHistoricalReasons=19,newIndividualDispositions=0,
        sourceCodeChanged=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,historicalRuntimeImportedAsCurrent=False,externalActions=0));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':main()
