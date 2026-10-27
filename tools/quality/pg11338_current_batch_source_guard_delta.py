"""Join one Batch source guard active finding scope and6 contexts to current original IDs without replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11306_current_batch_standard_text_delta import state as prior_state
from pg11329_batch_source_guard_context import inputs
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11338-current-batch-source-guard-delta-v1'
SOURCE='862cce50220c6ce186c084504756a7fbb9978270'


def state():
    ids,refs,pending=prior_state()
    m=data.read_checked(data.BASE/'PG11306-current-batch-standard-text-delta-v1/manifest.json','9ba4dac74123a2d5dcc71fa82547ef110f6310fbbbd1521adddf9ab852734dc8')
    d=data.read_checked(data.BASE/'PG11306-current-batch-standard-text-delta-v1/delta.json',m['deltaSha256'])
    scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']}
    new={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    ids-=set(d['removedFindingIds'])
    refs=(refs-scope)|new
    pending=(pending-scope)|new
    assert [len(ids),len(refs),len(pending)]==[8973,2755,158]
    return ids,refs,pending


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    ids,refs,pending=state()
    normal,original,actual=inputs()
    prior=data.read_checked(data.BASE/'PG11290-batch-standard-text-fixture-six-compile-v1/manifest.json','e5f2c258d8faa0b303f3d74edae30c3dfc03adc3e8964290ac022e5d140104d9')
    current={p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    changed={p:h for p,h in current.items() if prior['begin']['inputHashes'][p]!=h}
    assert len(current)==1810 and len(changed)==1 and all('/src/test/' in p for p in changed)
    context=data.read_checked(data.BASE/'PG11329-batch-source-guard-context-v1/manifest.json','fd78b2d6728898510ce9e585e0613a0477f8fd67be8a6298ac315aad633be6f7')
    rows=data.read_checked(data.BASE/'PG11329-batch-source-guard-context-v1/contexts.json',context['contextsSha256'])
    post=data.read_checked(data.BASE/'PG11331-batch-source-guard-context-post-v1/manifest.json','e8ec88ebb4a1fffad43de5f3b1ff47bcc46ad54bb437bd33092ccd2e4255bce6')
    assert post['actualExit']==0 and post['source']==SOURCE
    reviewed={r['id'] for r in rows}
    fresh=[]
    for path,node in actual:
        assert path in changed
        old=original_match(path,node,original,actual)
        assert old['id'] in reviewed or old['id'] in context['unclassifiedOriginalIds']
        fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',currentInputSha256=changed[path],rule=old['rule'],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],contextManifestSha256='fd78b2d6728898510ce9e585e0613a0477f8fd67be8a6298ac315aad633be6f7' if old['id'] in reviewed else None,
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING' if old['id'] in reviewed else 'UNCLASSIFIED_RETAINED',oldRuntimeReassigned=False))
    fresh_ids={r['id'] for r in fresh}
    original_scope={r['id'] for r in original if r['path'] in changed}
    scope=original_scope&ids
    assert len(original_scope)==25 and len(scope)==23 and len(scope&refs)==6 and len(scope&pending)==6
    assert all(r['rule']=='AvoidDuplicateLiterals' for r in original if r['id'] in original_scope-scope)
    assert len(fresh)==len(fresh_ids)==8 and len(reviewed)==6 and fresh_ids==reviewed|set(context['unclassifiedOriginalIds'])
    removed=scope-fresh_ids
    assert len(removed)==15 and all(r['rule']=='CloseResource' for r in original if r['id'] in removed)
    cr,cp=(refs-scope)|reviewed,(pending-scope)|reviewed
    assert [len(ids-removed),len(cr),len(cp),len((ids-removed)-cr)]==[8958,2755,158,6203]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),
        originalScopeFindings=25,previouslyRemovedIds=sorted(original_scope-scope),oldScopeFindings=23,newScopeFindings=8,replacedContextWarnings=6,newContextReferencesNet=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=1,otherSourcePathsUnchanged=1809,originalRaw=9409,priorDerivedRaw=8973,
        sourceDerivedRaw=8958,mainRaw=1512,testRaw=7446,totalPriorCorrections=451,sourceScopeCorrectionsAlreadyCounted=15,
        joinedContextWarnings=2755,sourceReboundCurrentWholePending=158,noCurrentReferenceInThisJoin=6203,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
