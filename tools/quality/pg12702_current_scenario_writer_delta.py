"""Three original condition corrections and six historical Thread context rebindings, no raw suppression."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12676_current_transfer_verifier_delta import state_after as previous_state

SOURCE='e353b1f49a740a426031fdc199f7ce8b26081971'
OUT=data.BASE/'PG12702-current-scenario-writer-delta-v1'
POST=data.BASE/'PG12703-current-scenario-writer-delta-post-v1'
REMOVED={'PMD-02649','PMD-02650','PMD-02651','PMD-02652','PMD-02653'}
REBOUND={'PMD-02647','PMD-02648'}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    assert REBOUND<=ids and REBOUND<=refs and not REBOUND&pending
    return ids-REMOVED,refs,pending|REBOUND


def expected():
    plan=data.read_checked(data.BASE/'PG12684-scenario-writer-plan-v1/manifest.json','71ae38137584d347696953a2ae460d1bb825a05a97dd1cbbb37ac794b4f58075')
    static=data.read_checked(data.BASE/'PG12690-scenario-writer-static-v1/manifest.json','17b8482c9fa40b627242b21a418ac385a925ecd66fe68ec57752ca7d0a666692')
    proof=data.read_checked(data.BASE/'PG12693-scenario-writer-post-v2/manifest.json','65934c65ce4836ce0f3b50c109a21ce3d327418a5eef9fad6926cf4b5352b872')
    review=data.read_checked(data.BASE/'PG12694-scenario-writer-context-v1/manifest.json','ffeadb4a1d3136f4b4fa9f3de29db1f4984add4900872cb2f2b0cef7e4a61415')
    post=data.read_checked(data.BASE/'PG12696-scenario-writer-context-post-v1/manifest.json','b2b8426c0078bc41d086ba0d7f1c4ff55b960ba9384df7928ce0c3a5355cfb6c')
    assert static['source']==proof['source']==review['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==review['actualExit']==post['actualExit']==0
    changes={r['path']:r for r in plan['sourceChanges']};assert static['sourceHashes']=={p:r['sha256'] for p,r in changes.items()}
    assert static['reports']['pmd']['findings']==2 and static['reports']['checkstyle']['findings']==0
    for label,v in static['reports'].items():
        assert v['processingErrors']==0;raw=(data.BASE/'PG12690-scenario-writer-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        nodes=[n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2]=='violation'];assert all(n.get('rule')=='DoNotUseThreads' for n in nodes)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    old_scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in old_scope}==REMOVED|REBOUND and len(old_scope)==7
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in old_scope)
    contexts=data.read_checked(data.BASE/'PG12694-scenario-writer-context-v1/review.json',review['reviewSha256'])['rows'];assert {r['id'] for r in contexts}==REBOUND and len(contexts)==2 and all(r['source']==SOURCE for r in contexts)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8493,3175,786,5318]
    assert len({r['id'] for r in original}-ids)==924 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=contexts,sourceReboundExistingContextIds=sorted(REBOUND),newClassificationIds=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=8493,mainRaw=1506,testRaw=6987,totalPriorCorrections=924,joinedContextWarnings=3175,sourceReboundCurrentWholePending=786,noCurrentReferenceInThisJoin=5318,oldScopeFindings=7,newScopeFindings=2,newContextClassifications=0,newSourceRebindings=2,staticActualExit=1,contextPostNegativeVectors=22,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',v)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(v):
        if v!=reference:raise ValueError('exact original raw/removal and existing-context source rebinding required')
    require(candidate);labels=[]
    for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('totalPriorCorrections',925),('newAccepted',1),('removedFindingIds',[]),('retainedIntroducedFindings',[]),('newContextClassifications',2),('newSourceRebindings',0),('staticActualExit',0)]:
        bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid source/removal/context credit accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8493,totalPriorCorrections=924,joinedContextWarnings=3175,sourceReboundCurrentWholePending=786,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
