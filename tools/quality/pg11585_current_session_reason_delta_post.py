"""Independent current IDs, historical reason availability and two concrete source facts; no JDBC execution."""
from collections import Counter
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11585-current-session-reason-delta-post-v1'

def require(value,expected):
    if value!=expected:
        raise ValueError('exact unchanged raw and44 concretely supported source references required')

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical()
    for folder,pin in [('PG11460-current-gc-fake-guard-delta-v1','3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2'),('PG11490-current-api-web-gc-literal-delta-v1','07d118026d90370f563c0aa28916a65f05da1b8b9936fef8591db487eddc6a12'),
        ('PG11520-current-metric-http-literal-delta-v1','e97204190f4e62c5fd8dc1135e011f5ee1f2dd3346c462aaf8983508d084b1ab'),('PG11552-current-memory-http-guard-delta-v1','27544edc188e17ec6ec38a7222dc8403298827e25762c67e56cee865e7b1e0bc'),('PG11564-current-batch-repository-reason-delta-v1','7f74d22280372600bb6c8287e831f2759108756310473dc64c7caac364042a0a'),('PG11574-current-four-repository-reason-delta-v1','7d8654ec83c6d8846b109ecb4a6cc11101fb13e904b0a722d96a727b2d316ffe')]:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8896,2985,426]
    mp=data.BASE/'PG11584-current-session-reason-delta-v1/manifest.json';manifest=data.read_checked(mp,'8007dfb863b96964ad4921ff916f0adb21c3121b8fd8394506017f59c3b43432');delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    cp=data.BASE/'PG11580-batch-session-source-review-v1/manifest.json';context=data.read_checked(cp,'198461923534abf92c0bb71cecb4c83bc98f5dd3f0b5228c67f95ca1c24dcadc');review=data.read_checked(cp.parent/'review.json',context['reviewSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');root={r['id']:r for r in original}
    old=data.read_checked(data.BASE/'PG6048-current-jdbc24-v2/findings.json','b1911fd378922d94ec8d2cae652b4a7559023fa584dbd6030355be907332f2cf')
    later=data.read_checked(data.BASE/'PG6354-batch-database-static-review-v1/decisions.json','38c60283328126fb4ee808d1566ce395c5083bbb8a2006a0af8733f471967bb9')
    sources={r['id']:r for r in review['rows']};assert len(sources)==44
    assert {r['id'] for r in delta['freshRows']}==set(sources)
    histories=Counter();new_kinds=Counter()
    for identity,row in sources.items():
        raw=root[identity];assert raw['path']==row['path'] and raw['attributes']==row['attributes'] and raw['rowSha256']==row['originalRowSha256']
        text=(data.ROOT/row['path']).read_text();assert data.sha(text.encode())==raw['inputSha256']==row['sourceSha256']
        rows=old if row['historicalManifest'].startswith('PG6048') else later
        found=[r for r in rows if r['findingId']==row['historicalFindingId']];assert len(found)==1;prior=found[0]
        assert prior['sourceSha256']==row['sourceSha256'] and prior['diagnosticTextSha256']==data.sha(raw['message'].encode())
        assert prior['sourcePath']==row['path'] and prior['rule']==raw['rule'] and all(str(prior[k])==str(raw['attributes'][k]) for k in ('beginline','endline','begincolumn','endcolumn','priority'))
        if prior.get('reason'):
            assert row['reason']==prior['reason'] and row['currentSourceFacts'] is None and not row['historicalReasonWasBlank'];histories['reused']+=1
        else:
            facts=row['currentSourceFacts'];assert row['historicalReasonWasBlank'] and row['reasonOrigin']=='CURRENT_TYPED_SOURCE_REVIEW' and row['reason']==facts['reason']
            assert facts['method']==raw['attributes']['method'] and facts['ownership']['nonnullGuard'] and facts['ownership']['directCloseCount']==1
            assert facts['ownership']['closeTypes']==['SQLException','RuntimeException','Error'] and not facts['ptExecution'] and not facts['actualDatabaseOrRootStateProven']
            lines=text.splitlines(keepends=True);a=raw['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
            assert data.sha(text[point:end].encode())==facts['sourceSpanSha256']
            ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];index=next(i for i,(_,pos) in enumerate(ts) if pos==point)
            ma,mb,name=min((s for s in functions(ts) if s[0]<=index<=s[1]),key=lambda s:s[1]-s[0]);assert name==facts['method']
            assert data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode())==facts['methodTokenSha256']
            method=''.join(t for t,_ in ts[ma:mb+1]);assert identity in ('PMD-03398','PMD-03399')
            assert 'catch(SQLException|RuntimeException|Errorprimary){failure=primary;throwprimary;}' in method
            assert 'if(JdbcResourceFailures.replace(failure,secondary))throwsecondary;' in method
            assert 'present(statement).execute("SET TRANSACTION READ ONLY");' in method and method.count('statement.close();')==1
            new_kinds[facts['kind']]+=1;histories['newSource']+=1
        assert row['rawWarningRetained'] and not row['ptExecutionExempt'] and row['productTestsExecuted']==0 and row['coverage'] is None and not row['oldRuntimeReassigned']
    assert histories==Counter(reused=42,newSource=2)
    assert new_kinds==Counter(CURRENT_TYPED_PRIMARY_CAPTURE_AND_SAME_IDENTITY_RETHROW=2)
    reviewed=set(sources);assert reviewed<=ids and not reviewed&refs and not reviewed&pending
    paths={r['path'] for r in sources.values()};excluded={r['id'] for r in original if r['path'] in paths and r['rule']=='DoNotUseThreads'}
    assert len(excluded)==4 and excluded<=refs and not excluded&reviewed
    assert not delta['removedFindingIds'] and not delta['addedFindingIds'] and not delta['sourceInputDelta']
    cr=refs|reviewed;cpending=pending|reviewed
    expected=dict(source=SOURCE,raw=len(ids),refs=len(cr),pending=len(cpending),withoutReference=len(ids-cr),reused=42,newSource=2,newPt=0)
    observed=dict(source=manifest['source'],raw=manifest['sourceDerivedRaw'],refs=manifest['joinedContextWarnings'],pending=manifest['sourceReboundCurrentWholePending'],withoutReference=manifest['noCurrentReferenceInThisJoin'],reused=manifest['reauthenticatedHistoricalReasons'],newSource=manifest['newSourcePointReviews'],newPt=manifest['productTestsExecuted'])
    require(observed,expected)
    for key,value in [('source','old'),('raw',8800),('refs',2841),('pending',282),('withoutReference',0),('reused',96),('newSource',0),('newPt',68)]:
        bad=copy.deepcopy(observed);bad[key]=value
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('reasonless label/old runtime falsely credited')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),counts=expected,metadataNegativeVectors=8,
        reviewed44=44,reauthenticatedHistoricalReasons=42,newSourcePointReviews=2,sourceCodeChanged=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,historicalRuntimeImportedAsCurrent=False,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
