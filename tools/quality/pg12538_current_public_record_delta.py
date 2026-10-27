"""New2 PT methods in already-zero Test; preserve all raw IDs, corrections, history and current pending."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12516_current_pure_resource_profile_delta import state as before_pure

SOURCE='03ffd8803faf780d872d002426c599a2a0a3814f'
OUT=data.BASE/'PG12538-current-public-record-delta-v1'


def state():
    ids,refs,pending=before_pure()
    p=data.BASE/'PG12516-current-pure-resource-profile-delta-v1'
    m=data.read_checked(p/'manifest.json','81475aec82b3f079d7c18081bb77369abd56de9568133479bb05646277144ea1')
    d=data.read_checked(p/'delta.json',m['deltaSha256'])
    removed=set(d['removedFindingIds']);reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    assert len(removed)==15 and len(reviewed)==9 and not d['addedFindingIds'] and reviewed<=refs and not reviewed&pending
    ids-=removed;pending|=reviewed
    assert [len(ids),len(refs),len(pending)]==[8526,3181,775]
    return ids,refs,pending


def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=state()
    normal=data.read_checked(data.BASE/'PG12528-public-record-six-compile-v1/manifest.json','59a22edd2c2584134bb3f2d4a5bc3de042d007afee84f6aa8e0bd17e8a24c735')
    previous=data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    changed={p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p]!=h}
    assert list(changed)==['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java']
    sp=data.BASE/'PG12532-public-record-static-v1';st=data.read_checked(sp/'manifest.json','8503bd587b5bf9116527d22f524e3e8857bd9c736201317960a12ac01fedb341')
    assert st['actualExit']==0 and st['source']==SOURCE and st['sourceHashes']==changed
    for label in ('pmd','checkstyle'):
        raw=(sp/(label+'.xml')).read_bytes();assert data.sha(raw)==st['reports'][label]['sha256'] and st['reports'][label]['findings']==st['reports'][label]['processingErrors']==0
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original_ids={r['id'] for r in original if r['path'] in changed}
    assert original_ids=={'PMD-04444'} and not original_ids&ids and len({r['id'] for r in original}-ids)==891
    assert len([i for i in ids if i.startswith('PMD-NEW-')])==8
    proof=data.read_checked(data.BASE/'PG12534-public-record-post-v1/manifest.json','a323962266faa692be827b8e169d837da893472cd8ae7f5c56f6b61b3ac1a2bc')
    assert proof['source']==SOURCE and proof['actualExit']==0 and proof['originalMethods']==proof['newMethods']==2
    verify(invocation);OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=[],removedFindingIds=[],addedFindingIds=[],originalScopeFindings=1,historicalScopeCorrectionsAlreadyCounted=1,oldScopeFindings=0,newScopeFindings=0,replacedContextWarnings=0,newProductExecutions=0,newClassificationIds=[]))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),changedSourcePaths=1,sourceDerivedRaw=8526,mainRaw=1512,testRaw=7014,totalPriorCorrections=891,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=0,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),newTechnicalTestIds=2,actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
