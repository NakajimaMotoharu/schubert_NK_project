"""Sixteen Test corrections plus four ownership applicability contexts; preserve all other raw IDs."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12806_current_api_policy_delta import state_after as previous_state

SOURCE='0124b5938a50f4ceea542486c336ba12146cb1b4'
OUT=data.BASE/'PG12830-current-exact-registry-delta-v1'
POST=data.BASE/'PG12832-current-exact-registry-delta-post-v1'
REMOVED={'PMD-02174'}
NEW={'PMD-00358','PMD-00359'}


def context_rows():
    manifest=data.read_checked(data.BASE/'PG12824-exact-registry-context-v1/manifest.json','c96c20868b97aaf236ac1209719c68d5bbfe88b8a12c8babb35204b7c5806774')
    assert manifest['source']==SOURCE and manifest['actualExit']==0
    return data.read_checked(data.BASE/'PG12824-exact-registry-context-v1/review.json',manifest['reviewSha256'])['rows']


def state_after():
    ids,refs,pending=previous_state()
    current={row['id'] for row in context_rows()}
    assert len(current)==9 and len(current&refs)==7 and current-refs==NEW
    assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending and current&pending=={'PMD-'+str(n).zfill(5) for n in range(2168,2174)}
    return ids-REMOVED,refs|NEW,pending|current


def expected():
    plan=data.read_checked(data.BASE/'PG12817-exact-registry-plan-v3/manifest.json','88a9d3eebc46f473fdc492e5ecdd8806b380aae78701312631019e40eb41e978')
    static=data.read_checked(data.BASE/'PG12840-exact-registry-caller-static-v1/manifest.json','bc41a92bde38e75c3589339c5c4ba3540c6199061767c48aeb8bd64199b07bd5')
    proof=data.read_checked(data.BASE/'PG12842-exact-registry-caller-post-v1/manifest.json','3ba0058d651605f37b1a03293001919b431ce83471ebc14464de1a14bbe00aa3')
    post=data.read_checked(data.BASE/'PG12826-exact-registry-context-post-v1/manifest.json','1ef6be7fa63772894cc8f8a540922e5a4d68805825a57145e4074649fc426bbd')
    assert static['source']==proof['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==post['actualExit']==0
    assert proof['observedTestExecutions']==19 and post['metadataNegativeVectors']==22
    changes={row['path']:row for row in plan['sourceChanges']}
    assert all(static['sourceHashes'][path]==row['sha256'] for path,row in changes.items()) and len(static['sourceHashes'])==3
    for label,row in static['reports'].items():
        assert row['processingErrors']==0 and row['findings']==(9 if label=='pmd' else 0)
        content=(data.BASE/'PG12840-exact-registry-caller-static-v1'/(label+'.xml')).read_bytes();assert data.sha(content)==row['sha256']
        warnings=[node for node in ET.fromstring(content).iter() if node.tag.rpartition('}')[2]=='violation']
        assert all(node.get('rule') in ['AvoidSynchronizedStatement','DoNotUseThreads','UseConcurrentHashMap'] for node in warnings)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope=[row for row in original if row['path'] in static['sourceHashes']]
    assert len(scope)==10 and all(row['inputSha256']==(changes[row['path']]['beforeSha256'] if row['path'] in changes else static['sourceHashes'][row['path']]) for row in scope)
    rows=context_rows();current={row['id'] for row in rows}
    assert len(rows)==9 and {row['id'] for row in scope}-current==REMOVED and NEW<=current
    assert all(row['source']==SOURCE and row['currentWholeJoinPending'] and row['disposition']=='CONTEXT_NOT_APPLICABLE' for row in rows)
    ids,refs,pending=state_after()
    assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8471,3180,830,5291]
    assert len({row['id'] for row in original}-ids)==946 and len([ident for ident in ids if ident.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=rows,newClassificationIds=sorted(NEW),newContextClassifications=2,newSourceRebindings=7,retainedIntroducedFindings=sorted(ident for ident in ids if ident.startswith('PMD-NEW-')),sourceDerivedRaw=8471,mainRaw=1505,testRaw=6966,totalPriorCorrections=946,joinedContextWarnings=3180,sourceReboundCurrentWholePending=830,noCurrentReferenceInThisJoin=5291,oldScopeFindings=10,newScopeFindings=9,contextPostNegativeVectors=22,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists()
    value=expected();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{key:value[key] for key in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','newContextClassifications','newSourceRebindings','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists()
    reference=expected();manifest=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert manifest['actualExit']==0 and manifest['source']==SOURCE and manifest['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(value):
        if value!=reference:
            raise ValueError('exact corrected ID and newly source-bound ownership context accounting required')
    require(candidate);labels=[]
    for field,bad_value in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('testRaw',0),('totalPriorCorrections',945),('newClassificationIds',[]),('newSourceRebindings',0),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[])]:
        bad=copy.deepcopy(reference);assert bad[field]!=bad_value;bad[field]=bad_value
        try:
            require(bad)
        except ValueError:
            labels.append(field)
        else:
            raise AssertionError('vacuous delta accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8471,totalPriorCorrections=946,joinedContextWarnings=3180,sourceReboundCurrentWholePending=830,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
