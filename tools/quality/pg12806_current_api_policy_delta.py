"""One original closed-fixture correction and two existing current-source context rebindings."""
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match
from pg12776_current_api_duration_delta import state_after as previous_state

SOURCE='2baca5740741adb7c676cb85a83f15d19de01083'
OUT=data.BASE/'PG12806-current-api-policy-delta-v1'
POST=data.BASE/'PG12808-current-api-policy-delta-post-v1'
REMOVED={'PMD-01968'}
CONTEXT={'PMD-01969','PMD-01970'}


def state_after():
    ids,refs,pending=previous_state()
    assert REMOVED|CONTEXT<=ids and REMOVED|CONTEXT<=refs and REMOVED|CONTEXT<=pending
    return ids-REMOVED,refs-REMOVED,pending-REMOVED


def mapped(directory,pin):
    m=data.read_checked(directory/'manifest.json',pin)
    raw=(directory/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256']
    nodes=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    return m,{original_match(path,node,original,nodes)['id'] for path,node in nodes}


def expected():
    plan=data.read_checked(data.BASE/'PG12790-api-policy-ownership-plan-v1/manifest.json','0678f561228d431c3af13dc3a91939c13424969827d0ce0e98fe36045b3c7f56')
    old,oldids=mapped(data.BASE/'PG12788-api-approved-static-v1','7fbc48e4144162a72ac99ba0de8d412ecc4e479f53ce37b141435428fad67e59')
    current,newids=mapped(data.BASE/'PG12796-api-policy-static-v1','1dc9a5c49dea77b9801b3a8c3c1beffaf849d0c0d5e16f78f98ee14b73ae39e0')
    proof=data.read_checked(data.BASE/'PG12798-api-policy-post-v1/manifest.json','b20fd41e7bbd0ca35b2bf110b65fb6a4918da18566d3d71a6e041a45c1ba7240')
    context=data.read_checked(data.BASE/'PG12800-api-policy-context-v1/manifest.json','d434f64a0a860a9c5fc2ab11bcbbeb2dfc91783f468585d7a515776b1904c87f')
    post=data.read_checked(data.BASE/'PG12802-api-policy-context-post-v1/manifest.json','668d70434fc0b258dcbc13d9237d9e761943404acfdfa7e3c14a110519954153')
    assert old['source']==plan['sourceBefore']=='639bbc777593cd98d95db1b0316e8113b40b886b' and old['actualExit']==current['actualExit']==1
    assert current['source']==proof['source']==context['source']==post['source']==SOURCE and proof['actualExit']==context['actualExit']==post['actualExit']==0
    assert oldids==REMOVED|CONTEXT and newids==CONTEXT and oldids-newids==REMOVED
    assert len(plan['sourceChanges'])==1 and plan['totalCorrections']==1 and plan['metadataNegativeVectors']==8
    change=plan['sourceChanges'][0]
    assert old['sourceHashes'][change['path']]==change['beforeSha256'] and current['sourceHashes'][change['path']]==change['sha256']
    assert proof['observedTestExecutions']==38 and proof['rawStatic']==2 and proof['spotbugsSixExit']==0 and post['metadataNegativeVectors']==22
    rows=data.read_checked(data.BASE/'PG12800-api-policy-context-v1/review.json',context['reviewSha256'])['rows']
    assert {row['id'] for row in rows}==CONTEXT and all(row['source']==SOURCE and row['currentWholeJoinPending'] for row in rows)
    ids,refs,pending=state_after();assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8472,3178,827,5294]
    return dict(source=SOURCE,removedFindingIds=sorted(REMOVED),addedFindingIds=[],freshRows=rows,newClassificationIds=[],newSourceRebindings=2,retainedIntroducedFindings=sorted(x for x in ids if x.startswith('PMD-NEW-')),sourceDerivedRaw=8472,mainRaw=1505,testRaw=6967,totalPriorCorrections=945,joinedContextWarnings=3178,sourceReboundCurrentWholePending=827,noCurrentReferenceInThisJoin=5294,oldScopeFindings=3,newScopeFindings=2,staticActualExit=1,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0,coverage=None)


def main():
    invocation=capture(__file__);assert not OUT.exists();value=expected();verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),**{k:value[k] for k in ['sourceDerivedRaw','mainRaw','testRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin','staticActualExit','actualViolationCount','wholeF03Accepted','productTestsExecuted','newAccepted']}))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__);assert not POST.exists();reference=expected();m=json.loads((OUT/'manifest.json').read_bytes());candidate=json.loads((OUT/'delta.json').read_bytes())
    assert m['actualExit']==0 and m['source']==SOURCE and m['deltaSha256']==data.sha((OUT/'delta.json').read_bytes())
    def require(value):
        if value!=reference:raise ValueError('exact raw correction and source-bound retained contexts required')
    require(candidate);labels=[]
    for field,value in [('source','0'*40),('sourceDerivedRaw',0),('mainRaw',0),('testRaw',0),('totalPriorCorrections',944),('newClassificationIds',['foreign']),('newSourceRebindings',0),('newAccepted',1),('wholeF03Accepted',True),('removedFindingIds',[]),('retainedIntroducedFindings',[])]:
        bad=copy.deepcopy(reference);assert bad[field]!=value;bad[field]=value
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('wrong correction/context accounting accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,sourceDerivedRaw=8472,totalPriorCorrections=945,joinedContextWarnings=3178,sourceReboundCurrentWholePending=827,actualViolationCount=None,wholeF03Accepted=False,productTestsExecuted=0,newAccepted=0));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
