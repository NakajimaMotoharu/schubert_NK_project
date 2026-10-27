"""Reauthenticate8 existing reasons and source-review40 labels in four explicitly reviewed repositories; no new code/PT or runtime reassignment."""
from collections import Counter
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg10398_role_view_preflight import canonical
from pg11569_four_repository_scope_facts import fact,span

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11570-batch-four-repository-source-review-v1'
POST=data.BASE/'PG11572-batch-four-repository-source-review-post-v1'
PRIMARY_SHA=None
FACTS_SHA='372375bf808bf1662391d1658aab99ef6886895d75db882dca812fa228964268'
FILES={f'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/{name}.java' for name in ('BackupStepRepository','CleanupStepRepository','InspectionSummaryRepository','RunReferenceRepository')}
COORDS=('beginline','endline','begincolumn','endcolumn','priority')

def evidence():
    old_manifest=data.read_checked(data.BASE/'PG6048-current-jdbc24-v2/manifest.json','087cc73138dcb3f91f082510c9c2b6dc6a8f390e569a4cbaba1f6d75fccf3c4a')
    old=data.read_checked(data.BASE/'PG6048-current-jdbc24-v2/findings.json','b1911fd378922d94ec8d2cae652b4a7559023fa584dbd6030355be907332f2cf')
    later_manifest=data.read_checked(data.BASE/'PG6354-batch-database-static-review-v1/manifest.json','33d467098f3881a2a92b4de30992f921c51f312eddd572a2bad2c8e2b231805a')
    later=data.read_checked(data.BASE/'PG6354-batch-database-static-review-v1/decisions.json','38c60283328126fb4ee808d1566ce395c5083bbb8a2006a0af8733f471967bb9')
    assert old_manifest['actualExit']==later_manifest['actualExit']==0
    normal=data.read_checked(data.BASE/'PG11536-memory-http-guard-six-compile-v1/manifest.json','038ace9c4a7187703381af22f7ecb5680f7b5d3adb2a07a242c579ca36019936')
    assert normal['source']==SOURCE and normal['actualExit']==0
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    return normal,original,old,later

def match(row,old,later):
    def same(item):
        return item['sourcePath']==row['path'] and item['rule']==row['rule'] and all(str(item[k])==str(row['attributes'][k]) for k in COORDS)
    candidates=[('PG6048',r) for r in old if same(r) and r['status']!='NOT_REVIEWED_CURRENT_SOURCE']
    if not candidates:
        candidates=[('PG6354',r) for r in later if same(r)]
    if len(candidates)!=1:
        raise ValueError('one exact already-reviewed historical disposition required')
    folder,historical=candidates[0]
    if historical['sourceSha256']!=row['inputSha256'] or historical['diagnosticTextSha256']!=data.sha(row['message'].encode()):
        raise ValueError('complete identical source and diagnostic text required; coordinates alone insufficient')
    return folder,historical

def review():
    normal,original,old,later=evidence();rows=[];counts=Counter();origins=Counter();reason_origins=Counter();new_reviews=0
    assert data.sha((data.ROOT/'tools/quality/pg11569_four_repository_scope_facts.py').read_bytes())==FACTS_SHA
    selected=[r for r in original if r['path'] in FILES and r['rule'] in ('CloseResource','AvoidCatchingGenericException','DoNotThrowExceptionInFinally')];assert len(selected)==48
    for path in FILES:
        current=(data.ROOT/path).read_bytes()
        for historical_source in ('8c869d7cea21d587b859b3e72e3516d9d2deb5c8','aed19c6dca368e9717309d6f744d7917c6b7b32c'):
            assert subprocess.check_output(['git','show',historical_source+':'+path],cwd=data.ROOT)==current
    for row in selected:
        folder,historical=match(row,old,later);status=historical['status']
        assert status in ('REQUIRED_CONTRACT','FALSE_POSITIVE') and historical['rawWarningRetained']
        historical_reason=historical.get('reason','')
        if historical_reason:
            reason=historical_reason;source_fact=None;reason_origin=folder
        else:
            assert status=='REQUIRED_CONTRACT'
            source_fact=fact(row);reason=source_fact['reason'];reason_origin='CURRENT_TYPED_SOURCE_REVIEW';new_reviews+=1
        assert reason
        reason_origins[reason_origin]+=1
        assert row['inputSha256']==normal['begin']['inputHashes'][row['path']]==data.sha((data.ROOT/row['path']).read_bytes())
        _,_,current_span=span((data.ROOT/row['path']).read_text(),row['attributes'])
        rows.append(dict(id=row['id'],path=row['path'],source=SOURCE,sourceSha256=row['inputSha256'],attributes=row['attributes'],originalRowSha256=row['rowSha256'],
            currentSpanSha256=data.sha(current_span.encode()),diagnosticTextSha256=data.sha(row['message'].encode()),disposition=status,
            historicalManifest='PG6048-current-jdbc24-v2/manifest.json' if folder=='PG6048' else 'PG6354-batch-database-static-review-v1/manifest.json',
            historicalFindingId=historical['findingId'],historicalReasonRowSha256=data.sha(json.dumps(historical,sort_keys=True).encode()),reason=reason,reasonOrigin=reason_origin,historicalReasonWasBlank=not bool(historical_reason),currentSourceFacts=source_fact,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',rawWarningRetained=True,ptExecutionExempt=False,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None))
        counts[status]+=1;origins[folder]+=1
    assert counts==Counter(REQUIRED_CONTRACT=40,FALSE_POSITIVE=8) and origins==Counter(PG6048=48)
    assert new_reviews==40 and reason_origins==Counter(PG6048=8,CURRENT_TYPED_SOURCE_REVIEW=40)
    assert data.sha((data.ROOT/'tools/quality/pg11569_four_repository_scope_facts.py').read_bytes())==FACTS_SHA
    helper='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/JdbcResourceFailures.java'
    fixed='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRepositoryException.java'
    for path in (helper,fixed):
        assert subprocess.check_output(['git','show','8c869d7cea21d587b859b3e72e3516d9d2deb5c8:'+path],cwd=data.ROOT)==(data.ROOT/path).read_bytes()
    compact=''.join(canonical((data.ROOT/helper).read_text()))
    assert 'if(primary==null||(primaryinstanceofSQLException&&!(secondaryinstanceofSQLException)))returntrue;' in compact
    assert 'if(!(primaryinstanceofSQLException))primary.addSuppressed(newBatchRepositoryException());returnfalse;' in compact
    ss='documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md'
    ss_bytes=subprocess.check_output(['git','show','origin/main:'+ss],cwd=data.ROOT)
    assert all(marker.encode() in ss_bytes for marker in ('SSC063/PG179','SSC063/PG181','SSC063/PG182','SQL primary','未知'))
    return dict(source=SOURCE,rows=rows,counts=dict(counts),historicalRecordOrigins=dict(origins),historicalReasonOrigins={k:v for k,v in reason_origins.items() if k!='CURRENT_TYPED_SOURCE_REVIEW'},currentSourceReviewFacts=40,factExtractorSha256=FACTS_SHA,normalManifestSha256='038ace9c4a7187703381af22f7ecb5680f7b5d3adb2a07a242c579ca36019936',
        mainSourceHashes={p:normal['begin']['inputHashes'][p] for p in sorted(FILES|{helper,fixed})},approvedDesign=dict(path=ss,originMainCommit=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),sha256=data.sha(ss_bytes)),
        reauthenticatedHistoricalReasons=8,newIndividualDispositions=40,sourceCodeChanged=False,historicalRuntimeImportedAsCurrent=False,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0)

def require(value,expected):
    if value!=expected:
        raise ValueError('all48 exact current source and eight historical reasons/forty new source facts; no new runtime qualification')

def main():
    invocation=capture(__file__);assert not OUT.exists();value=review()
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),reviewed=48,
        historicalRecordOrigins=value['historicalRecordOrigins'],historicalReasonOrigins=value['historicalReasonOrigins'],currentSourceReviewFacts=40,factExtractorSha256=FACTS_SHA,dispositions=value['counts'],reauthenticatedHistoricalReasons=8,newIndividualDispositions=40,sourceCodeChanged=False,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,historicalRuntimeImportedAsCurrent=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation=capture(__file__);assert not POST.exists();primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA);value=data.read_checked(OUT/'review.json',primary['reviewSha256']);expected=review();require(value,expected)
    bads=[]
    for key,v in [('source','old'),('reauthenticatedHistoricalReasons',100),('newIndividualDispositions',96),('sourceCodeChanged',True),('historicalRuntimeImportedAsCurrent',True),('productTestsExecuted',68),('coverage',100),('rawWarningsRemoved',16),('wholeF03Accepted',True)]:
        bad=copy.deepcopy(value);bad[key]=v;bads.append(bad)
    bad=copy.deepcopy(value);bad['rows'].pop();bads.append(bad)
    bad=copy.deepcopy(value);bad['rows'][0]['sourceSha256']='0'*64;bads.append(bad)
    bad=copy.deepcopy(value);bad['rows'][0]['disposition']='PASS';bads.append(bad)
    index=next(i for i,r in enumerate(value['rows']) if r['historicalReasonWasBlank'])
    bad=copy.deepcopy(value);bad['rows'][index]['reason']='';bads.append(bad)
    bad=copy.deepcopy(value);bad['rows'][index]['currentSourceFacts']=None;bads.append(bad)
    bad=copy.deepcopy(value);bad['currentSourceReviewFacts']=0;bads.append(bad)
    for bad in bads:
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('invented code/review/runtime or incomplete mapping accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,reviewSha256=primary['reviewSha256'],metadataNegativeVectors=len(bads),
        reviewed=48,reauthenticatedHistoricalReasons=8,newIndividualDispositions=40,sourceCodeChanged=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,
        historicalRuntimeImportedAsCurrent=False,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
