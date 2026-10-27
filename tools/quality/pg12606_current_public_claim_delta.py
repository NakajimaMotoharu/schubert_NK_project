"""Four original Test literal corrections and five historical Thread context rebindings, no raw suppression."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12582_current_public_unit_delta import state_after as previous_state

SOURCE='4749755f2562bd4e51658d8083a61e210ad2c521'
OUT=data.BASE/'PG12606-current-public-claim-delta-v1'
POST=data.BASE/'PG12608-current-public-claim-delta-post-v1'
REMOVED={'PMD-04624','PMD-05171','PMD-05205','PMD-05206'}
REBOUND={'PMD-05172','PMD-05173','PMD-05207','PMD-05208','PMD-05209'}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    assert REBOUND<=ids and REBOUND<=refs and not REBOUND&pending
    return ids-REMOVED,refs,pending|REBOUND


def expected():
    plan=data.read_checked(data.BASE/'PG12590-public-claim-plan-v1/manifest.json','b2f729a14961d7d0ae65185840764c973ce71fb6ca9b60ee8825abb3fda2a224')
    static=data.read_checked(data.BASE/'PG12596-public-claim-static-v1/manifest.json','ec931c42c87e54d25e8564e7dad14f117807d89dc6efe5f95601bdbf8dc0d0aa')
    proof=data.read_checked(data.BASE/'PG12598-public-claim-post-v1/manifest.json','e3eaf051b3be8e0e2b79e41a53fb7073258c60e0cfff922aa5d5237af6512f65')
    review=data.read_checked(data.BASE/'PG12600-public-claim-context-v1/manifest.json','9b7488a8dc73b398b0be7f6c0f3c63f32d5a5b4e67a58d2d3026af418bec7d25')
    post=data.read_checked(data.BASE/'PG12602-public-claim-context-post-v1/manifest.json','d14bb76bcb5e73a048f61040e20c0cafd7aca449f54eb65a1cc9bf8268ceb6df')
    assert static['source']==proof['source']==review['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==review['actualExit']==post['actualExit']==0
    changes={r['path']:r for r in plan['sourceChanges']};assert static['sourceHashes']=={p:r['sha256'] for p,r in changes.items()}
    assert static['reports']['pmd']['findings']==5 and static['reports']['checkstyle']['findings']==0
    for label,v in static['reports'].items():
        assert v['processingErrors']==0;raw=(data.BASE/'PG12596-public-claim-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        nodes=[n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2]=='violation'];assert all(n.get('rule')=='DoNotUseThreads' for n in nodes)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    old_scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in old_scope}==REMOVED|REBOUND and len(old_scope)==9
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in old_scope)
    contexts=data.read_checked(data.BASE/'PG12600-public-claim-context-v1/review.json',review['reviewSha256'])['rows'];assert {r['id'] for r in contexts}==REBOUND and len(contexts)==5 and all(r['source']==SOURCE for r in contexts)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8507,3175,774,5332]
    assert len({r['id'] for r in original}-ids)==910 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=contexts,sourceReboundExistingContextIds=sorted(REBOUND),newClassificationIds=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=8507,mainRaw=1506,testRaw=7001,totalPriorCorrections=910,joinedContextWarnings=3175,sourceReboundCurrentWholePending=774,noCurrentReferenceInThisJoin=5332,oldScopeFindings=9,newScopeFindings=5,newContextClassifications=0,newSourceRebindings=5,staticActualExit=1,contextPostNegativeVectors=22,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',v)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(v):
        if v!=reference:raise ValueError('exact original raw/removal and existing-context source rebinding required')
    require(candidate);labels=[]
    for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('totalPriorCorrections',911),('newAccepted',1),('removedFindingIds',[]),('retainedIntroducedFindings',[]),('newContextClassifications',5),('newSourceRebindings',0),('staticActualExit',0)]:
        bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid source/removal/context credit accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8507,totalPriorCorrections=910,joinedContextWarnings=3175,sourceReboundCurrentWholePending=774,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
