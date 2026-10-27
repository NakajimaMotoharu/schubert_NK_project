"""Independent immutable history and current zero-raw Test; do not count new PT as static corrections."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_saved_history_12424 import historical_to_12424

SOURCE='03ffd8803faf780d872d002426c599a2a0a3814f'
PIN='27d85af42dce30f8aa0dbc2e316d81cdb08aaf44a1a9a922624548a3d223f0ad'
OUT=data.BASE/'PG12540-current-public-record-delta-post-v1'


def require(value,expected):
    if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('current source and unchanged complete raw set; new PT is not static correction or formal credit')


def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical_to_12424()
    for folder,pin in [('PG12436-current-resource-compound-delta-v1','dd6bab9f8cbb6ba1d1bf6a031f0d194e3c61cb60f02017a4dc5bdd56060573f0'),('PG12462-current-config-template-delta-v1','2236248507325db831cd9af306660cdb5f251f21683118b9c80b72ac3d780b0f'),('PG12488-current-enum-catalog-delta-v1','9514312d8850dd0205e4d5318d71288d2be5b5343c11751c4c23045cca03ccc0'),('PG12516-current-pure-resource-profile-delta-v1','81475aec82b3f079d7c18081bb77369abd56de9568133479bb05646277144ea1')]:
        p=data.BASE/folder;m=data.read_checked(p/'manifest.json',pin);d=data.read_checked(p/'delta.json',m['deltaSha256']);assert not d['addedFindingIds']
        removed=set(d['removedFindingIds']);reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids-=removed;refs=(refs-removed)|reviewed;pending=(pending-removed)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8526,3181,775]
    prior=data.read_checked(data.BASE/'PG12518-current-pure-resource-profile-delta-post-v1/manifest.json','20c5c03dcf7ad375be7f07cb1547177d8ed1367d446450d1c4c1142404439bea')
    assert prior['sourceDerivedRaw']==len(ids) and prior['joinedContextWarnings']==len(refs) and prior['sourceReboundCurrentWholePending']==len(pending)
    p=data.BASE/'PG12538-current-public-record-delta-v1';m=data.read_checked(p/'manifest.json',PIN);d=data.read_checked(p/'delta.json',m['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG12528-public-record-six-compile-v1/manifest.json','59a22edd2c2584134bb3f2d4a5bc3de042d007afee84f6aa8e0bd17e8a24c735')
    previous=data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    changed={p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p]!=h}
    assert list(changed)==['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java'] and d['sourceInputDelta']==changed
    sp=data.BASE/'PG12532-public-record-static-v1';st=data.read_checked(sp/'manifest.json','8503bd587b5bf9116527d22f524e3e8857bd9c736201317960a12ac01fedb341')
    assert st['source']==SOURCE and st['actualExit']==0 and st['sourceHashes']==changed
    for label in ('pmd','checkstyle'):
        raw=(sp/(label+'.xml')).read_bytes();assert data.sha(raw)==st['reports'][label]['sha256'] and st['reports'][label]['findings']==st['reports'][label]['processingErrors']==0
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original_ids={r['id'] for r in original if r['path'] in changed};assert original_ids=={'PMD-04444'} and not original_ids&ids
    assert not d['removedFindingIds'] and not d['addedFindingIds'] and not d['freshRows'] and not d['newClassificationIds'] and d['historicalScopeCorrectionsAlreadyCounted']==1
    assert len({r['id'] for r in original}-ids)==891 and len([i for i in ids if i.startswith('PMD-NEW-')])==8
    expected=dict(actualExit=0,source=SOURCE,changedSourcePaths=1,sourceDerivedRaw=8526,mainRaw=1512,testRaw=7014,totalPriorCorrections=891,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,joinedContextWarnings=3181,sourceReboundCurrentWholePending=775,noCurrentReferenceInThisJoin=5345,newTechnicalTestIds=2,actualViolationCount=None,wholeF03Accepted=False,newAccepted=0,productTestsExecuted=0)
    require(m,expected);negative=0
    for field,wrong in [('source','0'*40),('sourceDerivedRaw',8511),('totalPriorCorrections',906),('totalIntroducedDiagnosticsRetained',0),('sourceReboundCurrentWholePending',766),('actualViolationCount',0),('wholeF03Accepted',True),('sourceScopeCorrectionsAlreadyCounted',2)]:
        assert expected[field]!=wrong;bad=dict(m);bad[field]=wrong
        try:require(bad,expected)
        except ValueError:negative+=1
        else:raise AssertionError('double-counted prior correction/new PT as raw fix accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=PIN,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),unreferenced=len(ids-refs),totalCorrections=891,allIntroducedDiagnosticsRetained=8,metadataNegativeVectors=negative,sourceCorrections=0,newTechnicalTestIds=2,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
