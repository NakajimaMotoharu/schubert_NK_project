"""Two fixture raw corrections, eight new Main applicability contexts and nine existing source rebindings."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12831_current_exact_registry_delta_v2 import state_after as previous_state

SOURCE='f8ad1ae16aa52db0119fefbad9e2cea6d6affe55'
OUT=data.BASE/'PG12860-current-monitor-sequence-delta-v1'
POST=data.BASE/'PG12862-current-monitor-sequence-delta-post-v1'
REMOVED={'PMD-04807','PMD-04865'}
NEW={'PMD-'+str(i).zfill(5) for i in [2959,2967,2968,2969,2970,2971,2972,2973]}


def context_rows():
    m=data.read_checked(data.BASE/'PG12854-monitor-sequence-context-v1/manifest.json','3273a1622d8a8121316e31c28821651d27b5f81db7944f4e62998d7cba75403e');assert m['source']==SOURCE and m['actualExit']==0
    return data.read_checked(data.BASE/'PG12854-monitor-sequence-context-v1/review.json',m['reviewSha256'])['rows']


def state_after():
    ids,refs,pending=previous_state();current={row['id'] for row in context_rows()}
    assert len(current)==17 and len(current&refs)==9 and current-refs==NEW and current&pending=={'PMD-02960'}
    assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    return ids-REMOVED,refs|NEW,pending|current


def expected():
    plan=data.read_checked(data.BASE/'PG12844-monitor-sequence-plan-v1/manifest.json','af75aa949766cfffb5342f11bcec67fd2e61c484d60dca63b83d2d7a48715568')
    static=data.read_checked(data.BASE/'PG12850-monitor-sequence-static-v1/manifest.json','77ddcdcd19da753042dca663d3940012a6ef1fdfae74bf463e546a122ff8c3e3')
    proof=data.read_checked(data.BASE/'PG12852-monitor-sequence-post-v1/manifest.json','a3297ed8bbdb614f3ffb237edb34638a45d2375eb8dab20ed852244f4e271923')
    post=data.read_checked(data.BASE/'PG12856-monitor-sequence-context-post-v1/manifest.json','aa4e7a66e1b83f630c11c08c2db119f54ef84e3d27853b83ffcbedea8c3ba3e7')
    assert static['source']==proof['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==post['actualExit']==0
    assert proof['observedTestExecutions']==24 and proof['selectedThreeMainCoverage100'] and post['metadataNegativeVectors']==24
    changes={row['path']:row for row in plan['sourceChanges']};assert len(changes)==plan['totalCorrections']==2
    assert all(static['sourceHashes'][path]==row['sha256'] for path,row in changes.items()) and len(static['sourceHashes'])==6
    for label,row in static['reports'].items():
        assert row['processingErrors']==0 and row['findings']==(17 if label=='pmd' else 0)
        content=(data.BASE/'PG12850-monitor-sequence-static-v1'/(label+'.xml')).read_bytes();assert data.sha(content)==row['sha256']
        assert all(node.get('rule') in ['AvoidSynchronizedStatement','AvoidCatchingGenericException','NullAssignment','DoNotUseThreads'] for node in ET.fromstring(content).iter() if node.tag.rpartition('}')[2]=='violation')
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    historical=[row for row in original if row['path'] in static['sourceHashes']];before_ids,_,_=previous_state();scope=[row for row in historical if row['id'] in before_ids]
    assert len(historical)==len(scope)==19
    registry=data.read_checked(data.BASE/'PG12828-exact-registry-trace-v1/manifest.json','14eac4d619670517db4a0c0c411845769a1e26049c3526cd38fe2310b84fcdbb');by={row['path']:row for row in registry['sourceRows']}
    assert all(by[path]['sha256']==(changes[path]['beforeSha256'] if path in changes else digest) and by[path]['canonicalOwner']==by[path]['canonicalCostOwner']=='WBS-P018-09' for path,digest in static['sourceHashes'].items())
    rows=context_rows();current={row['id'] for row in rows};assert {row['id'] for row in scope}-current==REMOVED and len(rows)==17
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8469,3188,846,5281]
    assert len({row['id'] for row in original}-ids)==948 and len([i for i in ids if i.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=rows,newClassificationIds=sorted(NEW),newContextClassifications=8,newSourceRebindings=9,retainedIntroducedFindings=sorted(i for i in ids if i.startswith('PMD-NEW-')),sourceDerivedRaw=8469,mainRaw=1505,testRaw=6964,totalPriorCorrections=948,joinedContextWarnings=3188,sourceReboundCurrentWholePending=846,noCurrentReferenceInThisJoin=5281,oldScopeFindings=19,newScopeFindings=17,historicalScopeRows=19,previouslyCorrectedScopeRows=0,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();value=expected();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:value[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes());assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(value):
        if value!=reference:raise ValueError('exact prior raw/source identities and new Main context accounting required')
    require(candidate);labels=[]
    for field,value in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('testRaw',0),('totalPriorCorrections',947),('newClassificationIds',[]),('newSourceRebindings',0),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[]),('actualViolationCount',0)]:
        bad=copy.deepcopy(reference);assert bad[field]!=value;bad[field]=value
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('wrong current delta accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8469,totalPriorCorrections=948,joinedContextWarnings=3188,sourceReboundCurrentWholePending=846,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
