"""Two fixture corrections and six new monitor/oracle contexts; keep16 thread rebindings and global raw."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg12860_current_monitor_sequence_delta import state_after as previous_state

SOURCE='105fd644e90918945607b3ac3e4962843c7762bf'
OUT=data.BASE/'PG12884-current-pure-health-lifecycle-delta-v1'
POST=data.BASE/'PG12886-current-pure-health-lifecycle-delta-post-v1'
REMOVED={'PMD-04685','PMD-04896'}
NEW={'PMD-'+str(i).zfill(5) for i in [2954,2955,2956,2976,2977,4687]}


def context_rows():
    m=data.read_checked(data.BASE/'PG12878-pure-health-lifecycle-context-v1/manifest.json','75365584df3268405f71f92cfd55ef22bb9c03352699882ddbe542286fe7eb69');assert m['source']==SOURCE and m['actualExit']==0
    return data.read_checked(data.BASE/'PG12878-pure-health-lifecycle-context-v1/review.json',m['reviewSha256'])['rows']


def state_after():
    ids,refs,pending=previous_state();current={row['id'] for row in context_rows()}
    assert len(current)==22 and len(current&refs)==16 and current-refs==NEW and current&pending=={'PMD-04858','PMD-04859'}
    assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    return ids-REMOVED,refs|NEW,pending|current


def expected():
    plan=data.read_checked(data.BASE/'PG12868-pure-health-lifecycle-plan-v1/manifest.json','e3b10e5565ac1d369b3693a5dc3c5b5c80f8022f8d29226d23c578721b64715b')
    static=data.read_checked(data.BASE/'PG12874-pure-health-lifecycle-static-v1/manifest.json','2369a8378b3be015e6ab03f034cbe38d4d4feb9d31797aa2119d13551fa2e90e')
    proof=data.read_checked(data.BASE/'PG12876-pure-health-lifecycle-post-v1/manifest.json','927664b9e53c777f78d399ca5448afce4e4b15c39870934a25a6529f809249d4')
    post=data.read_checked(data.BASE/'PG12880-pure-health-lifecycle-context-post-v1/manifest.json','bafd82a00b8366ece46209969ea91baa01f9b443f0b77e70cd61db85e888b251')
    assert static['source']==proof['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==post['actualExit']==0
    assert proof['observedTestExecutions']==38 and proof['selectedFourMainCoverage100'] and post['metadataNegativeVectors']==25
    changes={row['path']:row for row in plan['sourceChanges']};assert len(changes)==plan['totalCorrections']==2
    assert all(static['sourceHashes'][path]==row['sha256'] for path,row in changes.items()) and len(static['sourceHashes'])==9
    for label,row in static['reports'].items():
        assert row['processingErrors']==0 and row['findings']==(22 if label=='pmd' else 0)
        content=(data.BASE/'PG12874-pure-health-lifecycle-static-v1'/(label+'.xml')).read_bytes();assert data.sha(content)==row['sha256']
        assert all(node.get('rule') in ['AvoidSynchronizedStatement','DoNotUseThreads'] for node in ET.fromstring(content).iter() if node.tag.rpartition('}')[2]=='violation')
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    historical=[row for row in original if row['path'] in static['sourceHashes']];before_ids,_,_=previous_state();scope=[row for row in historical if row['id'] in before_ids];assert len(historical)==len(scope)==24
    registry=data.read_checked(data.BASE/'PG12858-monitor-sequence-trace-v1/manifest.json','05668fb67894a11ac8226baabd546fac403ee14525a393b04cb5b8011078e6cc');by={row['path']:row for row in registry['sourceRows']}
    assert all(by[path]['sha256']==(changes[path]['beforeSha256'] if path in changes else digest) and by[path]['canonicalOwner']==by[path]['canonicalCostOwner']=='WBS-P018-09' for path,digest in static['sourceHashes'].items())
    rows=context_rows();current={row['id'] for row in rows};assert {row['id'] for row in scope}-current==REMOVED and len(rows)==22
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8467,3194,866,5273]
    assert len({row['id'] for row in original}-ids)==950 and len([i for i in ids if i.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=rows,newClassificationIds=sorted(NEW),newContextClassifications=6,newMainContexts=5,newTestPrivateMonitorOracleContext=1,newSourceRebindings=16,retainedIntroducedFindings=sorted(i for i in ids if i.startswith('PMD-NEW-')),sourceDerivedRaw=8467,mainRaw=1505,testRaw=6962,totalPriorCorrections=950,joinedContextWarnings=3194,sourceReboundCurrentWholePending=866,noCurrentReferenceInThisJoin=5273,oldScopeFindings=24,newScopeFindings=22,historicalScopeRows=24,previouslyCorrectedScopeRows=0,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();value=expected();verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:value[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes());assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(value):
        if value!=reference:raise ValueError('exact before/source/raw IDs and current monitor/oracle context required')
    require(candidate);labels=[]
    for field,value in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('testRaw',0),('totalPriorCorrections',949),('newClassificationIds',[]),('newSourceRebindings',0),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[]),('actualViolationCount',0)]:
        bad=copy.deepcopy(reference);assert bad[field]!=value;bad[field]=value
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('wrong delta accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8467,totalPriorCorrections=950,joinedContextWarnings=3194,sourceReboundCurrentWholePending=866,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
