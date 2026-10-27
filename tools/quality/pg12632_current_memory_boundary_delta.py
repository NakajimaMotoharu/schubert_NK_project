"""Three original condition corrections and six historical Thread context rebindings, no raw suppression."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12606_current_public_claim_delta import state_after as previous_state

SOURCE='915a8ed153b00d76a80164d36f9ce5b86d645046'
OUT=data.BASE/'PG12632-current-memory-boundary-delta-v1'
POST=data.BASE/'PG12634-current-memory-boundary-delta-post-v1'
REMOVED={'PMD-06392','PMD-08702','PMD-08703'}
REBOUND={'PMD-06393','PMD-06394','PMD-06395','PMD-06396','PMD-08704','PMD-08705'}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    assert REBOUND<=ids and REBOUND<=refs and not REBOUND&pending
    return ids-REMOVED,refs,pending|REBOUND


def expected():
    plan=data.read_checked(data.BASE/'PG12616-memory-boundary-plan-v1/manifest.json','82e5f9364cd979f4aebeef8bd3a8b2c72a3f720e432637383210c5d57c394c16')
    static=data.read_checked(data.BASE/'PG12622-memory-boundary-static-v1/manifest.json','d4cf88fc455039623e235190936553ad1d55c420c047fc5f693646f02f8e6011')
    proof=data.read_checked(data.BASE/'PG12624-memory-boundary-post-v1/manifest.json','38a996b54b2ccbff75e0697c340f97883080a0292e880e742707765f124d436c')
    review=data.read_checked(data.BASE/'PG12626-memory-boundary-context-v1/manifest.json','28a41111573b2334cd70f720d5dfd8b311165180a3ce16854ad76b1b4d5a39f7')
    post=data.read_checked(data.BASE/'PG12628-memory-boundary-context-post-v1/manifest.json','8e70e55e3b30c4e608b26ab5b85e0e8a2476dd7a30b4d3ec94d563041a55266d')
    assert static['source']==proof['source']==review['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==review['actualExit']==post['actualExit']==0
    changes={r['path']:r for r in plan['sourceChanges']};assert static['sourceHashes']=={p:r['sha256'] for p,r in changes.items()}
    assert static['reports']['pmd']['findings']==6 and static['reports']['checkstyle']['findings']==0
    for label,v in static['reports'].items():
        assert v['processingErrors']==0;raw=(data.BASE/'PG12622-memory-boundary-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        nodes=[n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2]=='violation'];assert all(n.get('rule')=='DoNotUseThreads' for n in nodes)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    old_scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in old_scope}==REMOVED|REBOUND and len(old_scope)==9
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in old_scope)
    contexts=data.read_checked(data.BASE/'PG12626-memory-boundary-context-v1/review.json',review['reviewSha256'])['rows'];assert {r['id'] for r in contexts}==REBOUND and len(contexts)==6 and all(r['source']==SOURCE for r in contexts)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8504,3175,780,5329]
    assert len({r['id'] for r in original}-ids)==913 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=contexts,sourceReboundExistingContextIds=sorted(REBOUND),newClassificationIds=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=8504,mainRaw=1506,testRaw=6998,totalPriorCorrections=913,joinedContextWarnings=3175,sourceReboundCurrentWholePending=780,noCurrentReferenceInThisJoin=5329,oldScopeFindings=9,newScopeFindings=6,newContextClassifications=0,newSourceRebindings=6,staticActualExit=1,contextPostNegativeVectors=22,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',v)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(v):
        if v!=reference:raise ValueError('exact original raw/removal and existing-context source rebinding required')
    require(candidate);labels=[]
    for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('totalPriorCorrections',914),('newAccepted',1),('removedFindingIds',[]),('retainedIntroducedFindings',[]),('newContextClassifications',6),('newSourceRebindings',0),('staticActualExit',0)]:
        bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid source/removal/context credit accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8504,totalPriorCorrections=913,joinedContextWarnings=3175,sourceReboundCurrentWholePending=780,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
