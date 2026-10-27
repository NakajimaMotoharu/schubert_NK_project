"""Three original condition corrections and six historical Thread context rebindings, no raw suppression."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12632_current_memory_boundary_delta import state_after as previous_state

SOURCE='917f2e755d4912e522b9893e55aa272fd8e80934'
OUT=data.BASE/'PG12656-current-run-session-delta-v1'
POST=data.BASE/'PG12658-current-run-session-delta-post-v1'
REMOVED={'PMD-05278','PMD-09106','PMD-09107'}
REBOUND={'PMD-05279','PMD-05280','PMD-09108','PMD-09109'}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    assert REBOUND<=ids and REBOUND<=refs and not REBOUND&pending
    return ids-REMOVED,refs,pending|REBOUND


def expected():
    plan=data.read_checked(data.BASE/'PG12641-run-session-plan-v2/manifest.json','63f14299fff1e3e3ed7c267affe50aaf7e83986cb80923be5af0270f32251ec4')
    static=data.read_checked(data.BASE/'PG12646-run-session-static-v1/manifest.json','57f4f368562af361b544c8bd12504ac80f3f8f180412050b688ca286ee66f457')
    proof=data.read_checked(data.BASE/'PG12648-run-session-post-v1/manifest.json','ae842806398dcd99f061b059abf4930e837553995574fe60ab191b8b7a0b6530')
    review=data.read_checked(data.BASE/'PG12650-run-session-context-v1/manifest.json','554fd03716bf2f8ba8e2f34cb857284161be0c1dd8bb6e99939ffe839b4eb80d')
    post=data.read_checked(data.BASE/'PG12652-run-session-context-post-v1/manifest.json','cf24df3cdfba2e31863c32225969d098506253098043ca910f5388b42781e90e')
    assert static['source']==proof['source']==review['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==review['actualExit']==post['actualExit']==0
    changes={r['path']:r for r in plan['sourceChanges']};assert static['sourceHashes']=={p:r['sha256'] for p,r in changes.items()}
    assert static['reports']['pmd']['findings']==4 and static['reports']['checkstyle']['findings']==0
    for label,v in static['reports'].items():
        assert v['processingErrors']==0;raw=(data.BASE/'PG12646-run-session-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        nodes=[n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2]=='violation'];assert all(n.get('rule')=='DoNotUseThreads' for n in nodes)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    old_scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in old_scope}==REMOVED|REBOUND and len(old_scope)==7
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in old_scope)
    contexts=data.read_checked(data.BASE/'PG12650-run-session-context-v1/review.json',review['reviewSha256'])['rows'];assert {r['id'] for r in contexts}==REBOUND and len(contexts)==4 and all(r['source']==SOURCE for r in contexts)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8501,3175,784,5326]
    assert len({r['id'] for r in original}-ids)==916 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=contexts,sourceReboundExistingContextIds=sorted(REBOUND),newClassificationIds=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=8501,mainRaw=1506,testRaw=6995,totalPriorCorrections=916,joinedContextWarnings=3175,sourceReboundCurrentWholePending=784,noCurrentReferenceInThisJoin=5326,oldScopeFindings=7,newScopeFindings=4,newContextClassifications=0,newSourceRebindings=4,staticActualExit=1,contextPostNegativeVectors=22,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',v)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(v):
        if v!=reference:raise ValueError('exact original raw/removal and existing-context source rebinding required')
    require(candidate);labels=[]
    for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('totalPriorCorrections',917),('newAccepted',1),('removedFindingIds',[]),('retainedIntroducedFindings',[]),('newContextClassifications',4),('newSourceRebindings',0),('staticActualExit',0)]:
        bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid source/removal/context credit accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8501,totalPriorCorrections=916,joinedContextWarnings=3175,sourceReboundCurrentWholePending=784,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
