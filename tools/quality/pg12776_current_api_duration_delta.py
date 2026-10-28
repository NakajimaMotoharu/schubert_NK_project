"""Two actual Test literal corrections; preserve original raw diagnostics and unrelated pending sets."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12756_current_metric_context_delta import state_after as previous_state

SOURCE='639bbc777593cd98d95db1b0316e8113b40b886b'
OUT=data.BASE/'PG12776-current-api-duration-delta-v1'
POST=data.BASE/'PG12778-current-api-duration-delta-post-v1'
REMOVED={'PMD-01854','PMD-01855'}


def state_after():
    ids,refs,pending=previous_state();assert REMOVED<=ids and not REMOVED&refs and not REMOVED&pending
    return ids-REMOVED,refs-REMOVED,pending-REMOVED


def expected():
    p=data.read_checked(data.BASE/'PG12764-api-duration-plan-v1/manifest.json','a7410b3431bb0c3290a925dcbde0227ca2acb97311063cbe25a84c714e1853b3')
    s=data.read_checked(data.BASE/'PG12770-api-duration-static-v1/manifest.json','8c7065107e2011546757b549c2522c462afc9fdd36b2447265d6e590cb21fbdd')
    proof=data.read_checked(data.BASE/'PG12772-api-duration-post-v1/manifest.json','e82331f2ed803cff702ec1ae5b429b07c19d11aa5210b953a98f9de3e46e544a')
    assert s['source']==proof['source']==SOURCE and s['actualExit']==proof['actualExit']==0
    changes={r['path']:r for r in p['sourceChanges']};assert s['sourceHashes']=={path:r['sha256'] for path,r in changes.items()}
    for label,v in s['reports'].items():
        assert v['findings']==v['processingErrors']==0
        raw=(data.BASE/'PG12770-api-duration-static-v1'/(label+'.xml')).read_bytes();assert data.sha(raw)==v['sha256']
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope=[r for r in original if r['path'] in changes];assert {r['id'] for r in scope}==REMOVED and len(scope)==2
    assert all(r['inputSha256']==changes[r['path']]['beforeSha256'] for r in scope)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8473,3179,828,5294]
    assert len({r['id'] for r in original}-ids)==944 and len([x for x in ids if x.startswith('PMD-NEW-')])==8
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=[],retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=len(ids),mainRaw=1505,testRaw=6968,totalPriorCorrections=944,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),originalScopeRows=scope,oldScopeFindings=2,newScopeFindings=0,newClassificationIds=[],newAccepted=0,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();v=expected();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',v);data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:v[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}));print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(v):
        if v!=reference:raise ValueError('exact raw ID/state accounting and source-specific actual two correction evidence required')
    require(candidate);labels=[]
    for field,badvalue in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('totalPriorCorrections',945),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[])]:
        bad=copy.deepcopy(reference);assert bad[field]!=badvalue;bad[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('vacuous or invalid delta accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8473,totalPriorCorrections=944,joinedContextWarnings=3179,sourceReboundCurrentWholePending=828,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':main()
