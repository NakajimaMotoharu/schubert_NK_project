"""Three original condition corrections and six historical Thread context rebindings, no raw suppression."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12702_current_scenario_writer_delta import state_after as previous_state

SOURCE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
OUT=data.BASE/'PG12732-current-alert-threshold-delta-v1'
POST=data.BASE/'PG12734-current-alert-threshold-delta-post-v1'
REMOVED={'PMD-02957','PMD-04699'}
REBOUND={'PMD-04700','PMD-04701','PMD-04702','PMD-04703'}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    assert REBOUND<=ids and REBOUND<=refs and not REBOUND&pending
    return ids-REMOVED,refs,pending|REBOUND


def expected():
    plan=data.read_checked(data.BASE/'PG12716-alert-threshold-plan-v1/manifest.json','9f59c8646f08f5df99f88b599219640d5b4aa531b3e4c8dabeb733f5ae414500')
    static=data.read_checked(data.BASE/'PG12722-alert-threshold-static-v1/manifest.json','2cd61dcada2767e9c62b6e580d0e5e2215758471408d6e69833e9d6452996707')
    proof=data.read_checked(data.BASE/'PG12724-alert-threshold-post-v1/manifest.json','29794dc297f068c62bdc0444c535810c238adb66a17c12aa701b0e677250bf4c')
    review=data.read_checked(data.BASE/'PG12726-alert-threshold-context-v1/manifest.json','f6359bf01da291c5f348e690f1f0ebe2ba99e7fbfa1d0ed89fa6836396e33b47')
    post=data.read_checked(data.BASE/'PG12728-alert-threshold-context-post-v1/manifest.json','9b270b68bf8b92247e7e41dabed06f24b4d5bca4d15795b652674a5f3e13ca36')
    assert static['source']==proof['source']==review['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==review['actualExit']==post['actualExit']==0
    changes={r['path']:r for r in plan['sourceChanges']};assert static['sourceHashes']=={p:r['sha256'] for p,r in changes.items()}
    assert static['reports']['pmd']['findings']==4 and static['reports']['checkstyle']['findings']==0
    for label,v in static['reports'].items():
        assert v['processingErrors']==0;raw=(data.BASE/'PG12722-alert-threshold-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        nodes=[n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2]=='violation'];assert all(n.get('rule')=='DoNotUseThreads' for n in nodes)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    old_scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in old_scope}==REMOVED|REBOUND and len(old_scope)==6
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in old_scope)
    contexts=data.read_checked(data.BASE/'PG12726-alert-threshold-context-v1/review.json',review['reviewSha256'])['rows'];assert {r['id'] for r in contexts}==REBOUND and len(contexts)==4 and all(r['source']==SOURCE for r in contexts)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8491,3175,790,5316]
    assert len({r['id'] for r in original}-ids)==926 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=contexts,sourceReboundExistingContextIds=sorted(REBOUND),newClassificationIds=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=8491,mainRaw=1505,testRaw=6986,totalPriorCorrections=926,joinedContextWarnings=3175,sourceReboundCurrentWholePending=790,noCurrentReferenceInThisJoin=5316,oldScopeFindings=6,newScopeFindings=4,newContextClassifications=0,newSourceRebindings=4,staticActualExit=1,contextPostNegativeVectors=22,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


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
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8491,totalPriorCorrections=926,joinedContextWarnings=3175,sourceReboundCurrentWholePending=790,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
