"""Nine actual public Test corrections; preserve original raw diagnostics and unrelated pending sets."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12562_current_monitoring_main_delta import state_after as previous_state

SOURCE='2efcd4ac8e1b7681fdba0862f7392bbbba5d3f68'
OUT=data.BASE/'PG12582-current-public-unit-delta-v1'
POST=data.BASE/'PG12584-current-public-unit-delta-post-v1'
REMOVED={'PMD-05038','PMD-05199'}|{'PMD-'+str(i).zfill(5) for i in range(5607,5614)}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    return ids-REMOVED,refs-REMOVED,pending-REMOVED


def expected():
    p=data.read_checked(data.BASE/'PG12570-public-unit-plan-v1/manifest.json','5ec7235434a5c8ce0c379da9decc85975dd2db1e7c60a2252e56eb6f121ae9e4')
    s=data.read_checked(data.BASE/'PG12576-public-unit-static-v1/manifest.json','7ab10e270524f200cf1bd53597127f4709f0df92fe0a26ee3211e0a4e62b3806')
    proof=data.read_checked(data.BASE/'PG12578-public-unit-post-v1/manifest.json','911bc75b7c886d101fe93b9d07cd465d4bcc348ee0aaad4f2adb62e52eed9517')
    assert s['source']==proof['source']==SOURCE and s['actualExit']==proof['actualExit']==0
    changes={r['path']:r for r in p['sourceChanges']};assert s['sourceHashes']=={path:r['sha256'] for path,r in changes.items()}
    for label,v in s['reports'].items():
        assert v['findings']==v['processingErrors']==0
        raw=(data.BASE/'PG12576-public-unit-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in scope}==REMOVED and len(scope)==9
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in scope)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8511,3175,769,5336]
    assert len({r['id'] for r in original}-ids)==906 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=len(ids),mainRaw=1506,testRaw=7005,totalPriorCorrections=906,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),originalScopeRows=scope,oldScopeFindings=9,newScopeFindings=0,newClassificationIds=[],newAccepted=0,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',v);data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(v):
        if v!=reference:raise ValueError('exact raw ID/state accounting and source-specific actual nine correction evidence required')
    require(candidate);labels=[]
    for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('totalPriorCorrections',907),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[])]:
        bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('vacuous or invalid delta accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8511,totalPriorCorrections=906,joinedContextWarnings=3175,sourceReboundCurrentWholePending=769,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
