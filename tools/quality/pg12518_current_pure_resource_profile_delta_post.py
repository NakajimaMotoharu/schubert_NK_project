"""Independent immutable history, actual XML and exact fifteen removals/nine current reason rebindings."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_saved_history_12424 import historical_to_12424
from pg11054_api_request_context import original_match

SOURCE='c099786934c864f31a6fb520184366c22c84f6ea'
PIN='81475aec82b3f079d7c18081bb77369abd56de9568133479bb05646277144ea1'
OUT=data.BASE/'PG12518-current-pure-resource-profile-delta-post-v1'


def require(value,expected):
    if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('exact raw IDs/history/source rebindings; no invented quality credit')


def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical_to_12424()
    for folder,pin in [('PG12436-current-resource-compound-delta-v1','dd6bab9f8cbb6ba1d1bf6a031f0d194e3c61cb60f02017a4dc5bdd56060573f0'),('PG12462-current-config-template-delta-v1','2236248507325db831cd9af306660cdb5f251f21683118b9c80b72ac3d780b0f'),('PG12488-current-enum-catalog-delta-v1','9514312d8850dd0205e4d5318d71288d2be5b5343c11751c4c23045cca03ccc0')]:
        p=data.BASE/folder;m=data.read_checked(p/'manifest.json',pin);delta=data.read_checked(p/'delta.json',m['deltaSha256'])
        assert not delta['addedFindingIds']
        removed=set(delta['removedFindingIds']);reviewed={r['id'] for r in delta['freshRows'] if r['contextManifestSha256']}
        ids-=removed;refs=(refs-removed)|reviewed;pending=(pending-removed)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8541,3181,766]
    old=data.read_checked(data.BASE/'PG12490-current-enum-catalog-delta-post-v1/manifest.json','de92648d9efcd0e6d4df8427274c29bedbc5bba82f3bf493e939c08f17392ab9')
    assert old['sourceDerivedRaw']==len(ids) and old['joinedContextWarnings']==len(refs) and old['sourceReboundCurrentWholePending']==len(pending)
    p=data.BASE/'PG12516-current-pure-resource-profile-delta-v1';m=data.read_checked(p/'manifest.json',PIN);delta=data.read_checked(p/'delta.json',m['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    previous=data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    changed={p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p]!=h}
    assert len(changed)==4 and delta['sourceInputDelta']==changed
    sp=data.BASE/'PG12504-pure-resource-profile-static-v1';static=data.read_checked(sp/'manifest.json','133577cdab5e74deceb505cca099830b4b06afc1800fd986efc372031e74ef04')
    assert static['actualExit']==1 and static['source']==SOURCE and static['sourceHashes']==changed
    for label in ('pmd','checkstyle'):
        raw=(sp/(label+'.xml')).read_bytes();assert data.sha(raw)==static['reports'][label]['sha256'] and static['reports'][label]['processingErrors']==0
        assert static['reports'][label]['findings']==(9 if label=='pmd' else 0)
    actual=[(str(__import__('pathlib').Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.parse(sp/'pmd.xml').getroot() if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    reviewed={original_match(path,n,original,actual)['id'] for path,n in actual}
    assert len(reviewed)==9 and all(n.get('rule')=='DoNotUseThreads' for _,n in actual)
    scope={r['id'] for r in original if r['path'] in changed};removed=scope-reviewed
    expected_removed={'PMD-04444','PMD-06499','PMD-06500','PMD-06936','PMD-06937','PMD-06938','PMD-06942','PMD-06943','PMD-06944','PMD-06945','PMD-06946','PMD-06947','PMD-07116','PMD-07117','PMD-07118'}
    assert len(scope)==24 and removed==expected_removed and removed<=ids and not removed&(refs|pending)
    assert all(r['rule'] in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition') and r['inputSha256']==previous['begin']['inputHashes'][r['path']] for r in original if r['id'] in removed)
    cp=data.BASE/'PG12508-pure-resource-profile-context-v1';context=data.read_checked(cp/'manifest.json','36f949bf42338516cef966581451c0d8294054518606e2888cad53df47f51719');rows=data.read_checked(cp/'review.json',context['reviewSha256'])['rows']
    verified=data.read_checked(data.BASE/'PG12510-pure-resource-profile-context-post-v1/manifest.json','e82716db72a0148c01d8df05ecf122cb3377893557be6933fa87e2cbd70b3b80')
    assert context['source']==verified['source']==SOURCE and context['actualExit']==verified['actualExit']==0 and {r['id'] for r in rows}==reviewed
    expected_rows=[dict(id=r['id'],path=r['path'],rule=r['rule'],sourceSha256=r['sourceSha256'],contextManifestSha256='36f949bf42338516cef966581451c0d8294054518606e2888cad53df47f51719',contextManifestPath=str((cp/'manifest.json').relative_to(data.ROOT)),contextPostManifestSha256='e82716db72a0148c01d8df05ecf122cb3377893557be6933fa87e2cbd70b3b80') for r in sorted(rows,key=lambda r:r['id'])]
    assert delta['freshRows']==expected_rows and set(delta['removedFindingIds'])==removed and not delta['addedFindingIds'] and delta['newClassificationIds']==[]
    assert reviewed<=refs and not reviewed&pending
    ids-=removed;pending|=reviewed
    assert [len(ids),len(refs),len(pending),len(ids-refs)]==[8526,3181,775,5345] and len({r['id'] for r in original}-ids)==891
    expected=dict(actualExit=0,source=SOURCE,changedSourcePaths=4,sourceDerivedRaw=8526,mainRaw=1512,testRaw=7014,totalPriorCorrections=891,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=15,joinedContextWarnings=3181,sourceReboundCurrentWholePending=775,freshSourceContextRebindings=9,newClassificationCount=0,actualViolationCount=None,wholeF03Accepted=False,newAccepted=0,productTestsExecuted=0)
    require(m,expected);negatives=0
    for field,wrong in [('source','0'*40),('sourceDerivedRaw',8541),('totalPriorCorrections',876),('totalIntroducedDiagnosticsRetained',0),('joinedContextWarnings',3190),('sourceReboundCurrentWholePending',766),('actualViolationCount',0),('wholeF03Accepted',True)]:
        assert expected[field]!=wrong;bad=dict(m);bad[field]=wrong
        try:require(bad,expected)
        except ValueError:negatives+=1
        else:raise AssertionError('wrong current raw/history/context set accepted')
    assert len([i for i in ids if i.startswith('PMD-NEW-')])==8
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=PIN,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),unreferenced=len(ids-refs),totalCorrections=891,allIntroducedDiagnosticsRetained=8,metadataNegativeVectors=negatives,sourceCorrections=15,freshSourceContextRebindings=9,newClassificationCount=0,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
