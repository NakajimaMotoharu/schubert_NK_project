"""Six actual Main corrections; preserve original raw diagnostics and unrelated pending sets."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12538_current_public_record_delta import state as previous_state

SOURCE='fb1a22da2433c7909ceba05c7eeb07c879e52325'
OUT=data.BASE/'PG12562-current-monitoring-main-delta-v1'
POST=data.BASE/'PG12564-current-monitoring-main-delta-post-v1'
REMOVED={'PMD-'+str(i).zfill(5) for i in range(2961,2967)}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and REMOVED<=refs and REMOVED<=pending
    return ids-REMOVED,refs-REMOVED,pending-REMOVED


def expected():
    p=data.read_checked(data.BASE/'PG12548-monitoring-main-plan-v1/manifest.json','e1b73f8dda2d18379ba8edcf172709a520dab816d33a94458d90bffbd3157baf')
    s=data.read_checked(data.BASE/'PG12554-monitoring-main-static-v1/manifest.json','fb2fe41cab40003c4a052244dacd1d3036f48c0d6178066e4d576145ac08c812')
    proof=data.read_checked(data.BASE/'PG12560-monitoring-main-post-v3/manifest.json','4d3aa8a2243747ad1bd72ea6abc03df5edf377c6ee56d952d3258f292c97653c')
    assert s['source']==proof['source']==SOURCE and s['actualExit']==proof['actualExit']==0
    changes={r['path']:r for r in p['sourceChanges']};assert s['sourceHashes']=={path:r['sha256'] for path,r in changes.items()}
    for label,v in s['reports'].items():
        assert v['findings']==v['processingErrors']==0
        raw=(data.BASE/'PG12554-monitoring-main-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in scope}==REMOVED and len(scope)==6
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in scope)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8520,3175,769,5345]
    assert len({r['id'] for r in original}-ids)==897 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=len(ids),mainRaw=1506,testRaw=7014,totalPriorCorrections=897,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),originalScopeRows=scope,oldScopeFindings=6,newScopeFindings=0,newClassificationIds=[],newAccepted=0,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',v);data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(v):
        if v!=reference:raise ValueError('exact raw ID/state accounting and source-specific actual six correction evidence required')
    require(candidate);labels=[]
    for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('totalPriorCorrections',898),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[])]:
        bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('vacuous or invalid delta accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8520,totalPriorCorrections=897,joinedContextWarnings=3175,sourceReboundCurrentWholePending=769,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
