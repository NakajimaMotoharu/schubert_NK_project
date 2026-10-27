"""Join four supplied Web metric fixture findings and14 contexts to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11200_current_api_catalog_scalar_pool_delta import state as prior_state
from pg11217_web_supplied_metric_fixture_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11228-current-web-supplied-metric-delta-v1'
SOURCE='ae55baa85af2174fa01d73b62ad8899d3f44f306'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11200-current-api-catalog-scalar-pool-delta-v1/manifest.json','1d8c2b3ee0b29dab43497b317aaff2130f07adaf99af8cc7fdfca243f2aea73a')
    d=data.read_checked(data.BASE/'PG11200-current-api-catalog-scalar-pool-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[9068,2745,110]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11184-api-catalog-scalar-pool-six-compile-v1/manifest.json','b969eabaf6bc2a4ca11e09532164925246302c919c2cd2e6000b63fb42984a7b')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==4 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11217-web-supplied-metric-fixture-context-v1/manifest.json','35d8853adda2d4489b3a805793f09ca94de996bfe68ec7e8bdb321f492791cab')
    rows=data.read_checked(data.BASE/'PG11217-web-supplied-metric-fixture-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11219-web-supplied-metric-fixture-context-post-v1/manifest.json','bc889d966d644be0ab9ea4a4e72f24e44edebf9ad4a560ebc38d1b25867464b8')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='35d8853adda2d4489b3a805793f09ca94de996bfe68ec7e8bdb321f492791cab',
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    scope={r['id'] for r in original if r['path'] in changed}
    assert len(scope)==47 and scope<=ids and len(scope&refs)==8 and not scope&pending
    assert len(fresh)==len(fresh_ids)==len(reviewed)==14 and fresh_ids==reviewed
    removed=scope-fresh_ids
    assert len(removed)==33 and all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[9035,2751,124,6284]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        oldScopeFindings=47,newScopeFindings=14,replacedContextWarnings=8,newContextReferencesNet=6,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,originalRaw=9409,priorDerivedRaw=9068,
        sourceDerivedRaw=9035,mainRaw=1512,testRaw=7523,totalPriorCorrections=374,sourceScopeCorrectionsAlreadyCounted=33,
        joinedContextWarnings=2751,sourceReboundCurrentWholePending=124,noCurrentReferenceInThisJoin=6284,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
