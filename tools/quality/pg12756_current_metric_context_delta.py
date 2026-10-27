"""Sixteen Test corrections plus four ownership applicability contexts; preserve all other raw IDs."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12732_current_alert_threshold_delta import state_after as previous_state

SOURCE='f75d2fea05a98fe40d731d1a3046a64d20bbbb65'
OUT=data.BASE/'PG12756-current-metric-context-delta-v1'
POST=data.BASE/'PG12758-current-metric-context-delta-post-v1'
REMOVED={'PMD-01894','PMD-01895','PMD-01897','PMD-01898','PMD-01899','PMD-01904','PMD-01909','PMD-01915','PMD-08400','PMD-08401','PMD-08403','PMD-08404','PMD-08405','PMD-08410','PMD-08415','PMD-08421'}
NEW={'PMD-01896','PMD-01914','PMD-08402','PMD-08420'}


def context_rows():
    manifest=data.read_checked(data.BASE/'PG12750-metric-context-context-v1/manifest.json','4424f49ea3ed72c64cd7d2249c3759ae5012c0a36e7eca1bff9a87ddbee71ea8')
    assert manifest['source']==SOURCE and manifest['actualExit']==0
    return data.read_checked(data.BASE/'PG12750-metric-context-context-v1/review.json',manifest['reviewSha256'])['rows']


def state_after():
    ids,refs,pending=previous_state()
    current={row['id'] for row in context_rows()}
    assert len(current)==38 and len(current&refs)==34 and current-refs==NEW
    assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending and not current&pending
    return ids-REMOVED,refs|NEW,pending|current


def expected():
    plan=data.read_checked(data.BASE/'PG12743-metric-context-plan-v3/manifest.json','8f93b0e7cfe3fdcd9e6dacbd13d936cafcb335645a571815097540574c6b7dd4')
    static=data.read_checked(data.BASE/'PG12746-metric-context-static-v1/manifest.json','6ea3560962d32afd4d0921d7c81f2ef47f101c3c7aca7bca3f0c0ab38f6b9e75')
    proof=data.read_checked(data.BASE/'PG12748-metric-context-post-v1/manifest.json','01190b958bf4c5fa867e158b1a5642f014eb57aae4df5353a01d3109cfb14486')
    post=data.read_checked(data.BASE/'PG12752-metric-context-context-post-v1/manifest.json','edbecc33de2ad980274691ba638bf147cd882904c889fb7350e7610bddd5a524')
    assert static['source']==proof['source']==post['source']==SOURCE and static['actualExit']==1 and proof['actualExit']==post['actualExit']==0
    assert proof['observedTestExecutions']==66 and post['metadataNegativeVectors']==24
    changes={row['path']:row for row in plan['sourceChanges']}
    assert static['sourceHashes']=={path:row['sha256'] for path,row in changes.items()}
    for label,row in static['reports'].items():
        assert row['processingErrors']==0 and row['findings']==(38 if label=='pmd' else 0)
        content=(data.BASE/'PG12746-metric-context-static-v1'/(label+'.xml')).read_bytes();assert data.sha(content)==row['sha256']
        warnings=[node for node in ET.fromstring(content).iter() if node.tag.rpartition('}')[2]=='violation']
        assert all(node.get('rule') in ['CloseResource','DoNotUseThreads'] for node in warnings)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope=[row for row in original if row['path'] in changes]
    assert len(scope)==54 and all(row['inputSha256']==changes[row['path']]['beforeSha256'] for row in scope)
    rows=context_rows();current={row['id'] for row in rows}
    assert len(rows)==38 and {row['id'] for row in scope}-current==REMOVED and NEW<=current
    assert all(row['source']==SOURCE and row['currentWholeJoinPending'] and row['disposition']=='CONTEXT_NOT_APPLICABLE' for row in rows)
    ids,refs,pending=state_after()
    assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8475,3179,828,5296]
    assert len({row['id'] for row in original}-ids)==942 and len([ident for ident in ids if ident.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=rows,newClassificationIds=sorted(NEW),newContextClassifications=4,newSourceRebindings=34,retainedIntroducedFindings=sorted(ident for ident in ids if ident.startswith('PMD-NEW-')),sourceDerivedRaw=8475,mainRaw=1505,testRaw=6970,totalPriorCorrections=942,joinedContextWarnings=3179,sourceReboundCurrentWholePending=828,noCurrentReferenceInThisJoin=5296,oldScopeFindings=54,newScopeFindings=38,contextPostNegativeVectors=24,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


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
    for field,bad_value in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('testRaw',0),('totalPriorCorrections',943),('newClassificationIds',[]),('newSourceRebindings',0),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[])]:
        bad=copy.deepcopy(reference);assert bad[field]!=bad_value;bad[field]=bad_value
        try:
            require(bad)
        except ValueError:
            labels.append(field)
        else:
            raise AssertionError('vacuous delta accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8475,totalPriorCorrections=942,joinedContextWarnings=3179,sourceReboundCurrentWholePending=828,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
