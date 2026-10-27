"""Independent current IDs, historical nonempty reasons for exact22 remaining Main warnings; no JDBC execution."""
from collections import Counter
import copy
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11605-current-remaining-main-reason-delta-post-v1'

def require(value,expected):
    if value!=expected:
        raise ValueError('exact unchanged raw and22 nonempty supported source references required')

def negative(observed,key,value):
    bad=copy.deepcopy(observed);bad[key]=value
    if bad==observed:raise ValueError('negative vector must differ from observed')
    return bad

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical()
    for folder,pin in [('PG11460-current-gc-fake-guard-delta-v1','3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2'),('PG11490-current-api-web-gc-literal-delta-v1','07d118026d90370f563c0aa28916a65f05da1b8b9936fef8591db487eddc6a12'),
        ('PG11520-current-metric-http-literal-delta-v1','e97204190f4e62c5fd8dc1135e011f5ee1f2dd3346c462aaf8983508d084b1ab'),('PG11552-current-memory-http-guard-delta-v1','27544edc188e17ec6ec38a7222dc8403298827e25762c67e56cee865e7b1e0bc'),('PG11564-current-batch-repository-reason-delta-v1','7f74d22280372600bb6c8287e831f2759108756310473dc64c7caac364042a0a'),('PG11574-current-four-repository-reason-delta-v1','7d8654ec83c6d8846b109ecb4a6cc11101fb13e904b0a722d96a727b2d316ffe'),('PG11584-current-session-reason-delta-v1','8007dfb863b96964ad4921ff916f0adb21c3121b8fd8394506017f59c3b43432'),('PG11594-current-admission-reason-delta-v1','877f695001a733ead184d078282c4f745836b7261b4628c09782919a1917f4b8')]:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8896,3048,489]
    mp=data.BASE/'PG11604-current-remaining-main-reason-delta-v2/manifest.json';manifest=data.read_checked(mp,'32fc3e82b65c092166fa54ee9848d398cf5d832908823be129796170371f73ce');delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    cp=data.BASE/'PG11600-remaining-main-source-reauth-v4/manifest.json';context=data.read_checked(cp,'09fbb963cf1a85c92357ffc42dea91852a443e4d1175e606f5cd82f160ffa442');review=data.read_checked(cp.parent/'review.json',context['reviewSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');root={r['id']:r for r in original}
    old=data.read_checked(data.BASE/'PG6048-current-jdbc24-v2/findings.json','b1911fd378922d94ec8d2cae652b4a7559023fa584dbd6030355be907332f2cf')
    later=data.read_checked(data.BASE/'PG6354-batch-database-static-review-v1/decisions.json','38c60283328126fb4ee808d1566ce395c5083bbb8a2006a0af8733f471967bb9')
    sources={r['id']:r for r in review['rows']};assert len(sources)==22
    assert {r['id'] for r in delta['freshRows']}==set(sources)
    histories=Counter()
    for identity,row in sources.items():
        raw=root[identity];assert raw['path']==row['path'] and raw['attributes']==row['attributes'] and raw['rowSha256']==row['originalRowSha256']
        text=(data.ROOT/row['path']).read_text();assert data.sha(text.encode())==raw['inputSha256']==row['sourceSha256']
        rows=old if row['historicalManifest'].startswith('PG6048') else later
        found=[r for r in rows if r['findingId']==row['historicalFindingId']];assert len(found)==1;prior=found[0]
        assert prior['sourceSha256']==row['sourceSha256'] and prior['diagnosticTextSha256']==data.sha(raw['message'].encode())
        assert prior['sourcePath']==row['path'] and prior['rule']==raw['rule'] and all(str(prior[k])==str(raw['attributes'][k]) for k in ('beginline','endline','begincolumn','endcolumn','priority'))
        expected_origin='8c869d7cea21d587b859b3e72e3516d9d2deb5c8' if row['historicalManifest'].startswith('PG6048') else 'aed19c6dca368e9717309d6f744d7917c6b7b32c'
        assert row['historicalSource']==expected_origin and prior['status']==row['disposition']
        assert subprocess.check_output(['git','show',expected_origin+':'+row['path']],cwd=data.ROOT)==text.encode()
        assert prior.get('reason') and row['reason']==prior['reason'] and row['currentSourceFacts'] is None and not row['historicalReasonWasBlank'];histories['reused']+=1
        assert row['rawWarningRetained'] and not row['ptExecutionExempt'] and row['productTestsExecuted']==0 and row['coverage'] is None and not row['oldRuntimeReassigned']
    assert histories==Counter(reused=22)
    reviewed=set(sources);assert reviewed<=ids and not reviewed&refs and not reviewed&pending
    paths={r['path'] for r in sources.values()};excluded={r['id'] for r in original if r['path'] in paths and r['rule']=='DoNotUseThreads'}
    assert not excluded&reviewed and excluded<=ids
    assert not delta['removedFindingIds'] and not delta['addedFindingIds'] and not delta['sourceInputDelta']
    cr=refs|reviewed;cpending=pending|reviewed
    expected=dict(source=SOURCE,raw=len(ids),refs=len(cr),pending=len(cpending),withoutReference=len(ids-cr),reused=22,newSource=0,newPt=0)
    observed=dict(source=manifest['source'],raw=manifest['sourceDerivedRaw'],refs=manifest['joinedContextWarnings'],pending=manifest['sourceReboundCurrentWholePending'],withoutReference=manifest['noCurrentReferenceInThisJoin'],reused=manifest['reauthenticatedHistoricalReasons'],newSource=manifest['newSourcePointReviews'],newPt=manifest['productTestsExecuted'])
    require(observed,expected)
    try:negative(observed,'newSource',observed['newSource'])
    except ValueError:pass
    else:raise AssertionError('same-value negative was allowed')
    assert negative(observed,'newSource',2)!=observed
    for key,value in [('source','old'),('raw',8800),('refs',2841),('pending',282),('withoutReference',0),('reused',96),('newSource',2),('newPt',68)]:
        bad=negative(observed,key,value)
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('reasonless label/old runtime falsely credited')
    assert 'PMD-06163' in reviewed and 'PMD-06162' in refs and 'PMD-06162' not in reviewed
    for bad in ((reviewed-{'PMD-06163'})|{'PMD-06162'},reviewed-{'PMD-06163'}):
        try:require(bad,reviewed)
        except ValueError:pass
        else:raise AssertionError('old referenced or missing ID accepted')
    failures=[]
    for path,pin,folder in [('tools/quality/pg11600_remaining_main_source_reauth.py','4b294e3d4907b8e60df93e6d63dcf3fd016e4f78017bb74d5071c77540ea4bf0','PG11600-remaining-main-source-reauth-v1'),('tools/quality/pg11600_remaining_main_source_reauth_v3.py','4fa2c763e9f5d28d6d55191b46f5bb65db6153d78bec44289a24e1f4df1d1000','PG11600-remaining-main-source-reauth-v3'),('tools/quality/pg11604_current_remaining_main_reason_delta.py','8f413b7a132d94d1fd067ab6edf0044e07d962565160a70bf540ea6675efc103','PG11604-current-remaining-main-reason-delta-v1')]:
        assert data.sha((data.ROOT/path).read_bytes())==pin and not (data.BASE/folder).exists();failures.append(dict(tool=path,sha256=pin,actualExit=1,outCreated=False))
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),counts=expected,metadataNegativeVectors=8,
        negativeGeneratorRegressionVectors=2,candidateIdentityNegativeVectors=2,preservedFailures=failures,
        reviewed22=22,reauthenticatedHistoricalReasons=22,newSourcePointReviews=0,sourceCodeChanged=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,historicalRuntimeImportedAsCurrent=False,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
