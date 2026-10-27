"""Exact15 fixture corrections; nine retained original thread reasons rebound, not new classification."""
import xml.etree.ElementTree as ET
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12488_current_enum_catalog_delta import state as before_enum

SOURCE='c099786934c864f31a6fb520184366c22c84f6ea'
OUT=data.BASE/'PG12516-current-pure-resource-profile-delta-v1'


def state():
    ids,refs,pending=before_enum()
    p=data.BASE/'PG12488-current-enum-catalog-delta-v1/manifest.json'
    m=data.read_checked(p,'9514312d8850dd0205e4d5318d71288d2be5b5343c11751c4c23045cca03ccc0')
    d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    removed=set(d['removedFindingIds'])
    assert removed=={'PMD-05808','PMD-06923','PMD-06924','PMD-06925','PMD-06926'} and not d['freshRows'] and not d['addedFindingIds']
    ids-=removed
    assert [len(ids),len(refs),len(pending)]==[8541,3181,766]
    return ids,refs,pending


def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    previous=data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    changed={p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p]!=h}
    plan=data.read_checked(data.BASE/'PG12496-pure-resource-profile-plan-v1/manifest.json','2afc6237ad922fab24e622ab94b8c9886518bcd742ec76041eb54a1c49f42f14')
    assert len(changed)==4 and changed=={r['path']:r['sha256'] for r in plan['sourceChanges']}
    sp=data.BASE/'PG12504-pure-resource-profile-static-v1'
    st=data.read_checked(sp/'manifest.json','133577cdab5e74deceb505cca099830b4b06afc1800fd986efc372031e74ef04')
    assert st['actualExit']==1 and st['source']==SOURCE and st['sourceHashes']==changed
    xml=(sp/'pmd.xml').read_bytes();assert data.sha(xml)==st['reports']['pmd']['sha256']
    nodes=[n for n in ET.fromstring(xml).iter() if n.tag.rpartition('}')[2]=='violation']
    assert len(nodes)==9 and all(n.get('rule')=='DoNotUseThreads' for n in nodes)
    assert st['reports']['checkstyle']['findings']==0 and all(v['processingErrors']==0 for v in st['reports'].values())
    assert data.sha((sp/'checkstyle.xml').read_bytes())==st['reports']['checkstyle']['sha256']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope={r['id'] for r in original if r['path'] in changed};removed={c['id'] for r in plan['sourceChanges'] for c in r['constants']}
    assert len(scope)==24 and len(removed)==15 and removed<=ids and not removed&(refs|pending)
    assert all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') and r['inputSha256']==previous['begin']['inputHashes'][r['path']] for r in original if r['id'] in removed)
    cp=data.BASE/'PG12508-pure-resource-profile-context-v1'
    context=data.read_checked(cp/'manifest.json','36f949bf42338516cef966581451c0d8294054518606e2888cad53df47f51719')
    review=data.read_checked(cp/'review.json',context['reviewSha256'])['rows']
    post=data.read_checked(data.BASE/'PG12510-pure-resource-profile-context-post-v1/manifest.json','e82716db72a0148c01d8df05ecf122cb3377893557be6933fa87e2cbd70b3b80')
    reviewed={r['id'] for r in review}
    assert context['actualExit']==post['actualExit']==0 and context['source']==post['source']==SOURCE and scope-removed==reviewed and len(reviewed)==9
    assert reviewed<=refs and not reviewed&pending and all(r['sourceSha256']==hashes[r['path']] for r in review)
    ids-=removed;refs|=reviewed;pending|=reviewed
    assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8526,3181,775,5345]
    assert len({r['id'] for r in original}-ids)==891 and len([i for i in ids if i.startswith('PMD-NEW-')])==8
    fresh=[dict(id=r['id'],path=r['path'],rule=r['rule'],sourceSha256=r['sourceSha256'],contextManifestSha256='36f949bf42338516cef966581451c0d8294054518606e2888cad53df47f51719',contextManifestPath=str((cp/'manifest.json').relative_to(data.ROOT)),contextPostManifestSha256='e82716db72a0148c01d8df05ecf122cb3377893557be6933fa87e2cbd70b3b80') for r in sorted(review,key=lambda r:r['id'])]
    assert all(Path(r['path']).suffix=='.java' for r in fresh)
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=fresh,removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=24,oldScopeFindings=24,newScopeFindings=9,replacedContextWarnings=9,newClassificationIds=[],newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),changedSourcePaths=4,sourceDerivedRaw=8526,mainRaw=1512,testRaw=7014,totalPriorCorrections=891,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=15,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),freshSourceContextRebindings=9,newClassificationCount=0,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
