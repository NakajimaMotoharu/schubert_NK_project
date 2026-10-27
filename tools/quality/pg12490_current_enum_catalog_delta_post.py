"""Independent immutable prior history, exact five removals and actual selected zero-raw reports."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_saved_history_12424 import historical_to_12424

SOURCE = '6929166ee735effb5cae211e1f4cfe44f0b97a0a'
PIN = '9514312d8850dd0205e4d5318d71288d2be5b5343c11751c4c23045cca03ccc0'
OUT = data.BASE/'PG12490-current-enum-catalog-delta-post-v1'

def require(value,expected):
    if any(value.get(k) != v for k,v in expected.items()):
        raise ValueError('exact current five removals and retained prior history/no formal credit required')

def main():
    invocation = capture(__file__);assert not OUT.exists();ids,refs,pending = historical_to_12424()
    p = data.BASE/'PG12436-current-resource-compound-delta-v1/manifest.json';before = data.read_checked(p,'dd6bab9f8cbb6ba1d1bf6a031f0d194e3c61cb60f02017a4dc5bdd56060573f0');d = data.read_checked(p.parent/'delta.json',before['deltaSha256'])
    assert not d['removedFindingIds'] and not d['addedFindingIds'];reviewed = {r['id'] for r in d['freshRows'] if r['contextManifestSha256']};assert len(reviewed) == 46
    refs |= reviewed;pending |= reviewed;assert [len(ids),len(refs),len(pending)] == [8553,3181,766]
    verified = data.read_checked(data.BASE/'PG12438-current-resource-compound-delta-post-v1/manifest.json','6d6ca0d4abafa17df506e10ebeb3b64e17e92e91d2a1117e0ca70ea6c9b44a56');assert verified['sourceDerivedRaw'] == len(ids) and verified['joinedContextWarnings'] == len(refs) and verified['sourceReboundCurrentWholePending'] == len(pending)
    prior_path=data.BASE/'PG12462-current-config-template-delta-v1'
    prior=data.read_checked(prior_path/'manifest.json','2236248507325db831cd9af306660cdb5f251f21683118b9c80b72ac3d780b0f')
    olddelta=data.read_checked(prior_path/'delta.json',prior['deltaSha256'])
    oldremoved=set(olddelta['removedFindingIds']);assert oldremoved=={f'PMD-{n:05}' for n in range(5240,5247)} and not olddelta['freshRows'] and not olddelta['addedFindingIds']
    ids-=oldremoved;assert [len(ids),len(refs),len(pending)]==[8546,3181,766]
    previouspost=data.read_checked(data.BASE/'PG12464-current-config-template-delta-post-v1/manifest.json','d7b109965ed1eb4a30e1f52c697c191e65c9623c23b7a88cc004d67eb1c247e3')
    assert previouspost['sourceDerivedRaw']==len(ids)
    p=data.BASE/'PG12488-current-enum-catalog-delta-v1';m=data.read_checked(p/'manifest.json',PIN);delta=data.read_checked(p/'delta.json',m['deltaSha256'])
    normal = data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe')
    previous = data.read_checked(data.BASE/'PG12450-config-template-six-compile-v1/manifest.json','face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0 and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    changed = {p:h for p,h in normal['begin']['inputHashes'].items() if previous['begin']['inputHashes'][p] != h}
    assert set(changed) == {'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/EnumValueCatalogCompatibilityTest.java','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/EnumValueCatalogCompatibilityTest.java'} and delta['sourceInputDelta'] == changed
    sp = data.BASE/'PG12480-enum-catalog-static-v1';st = data.read_checked(sp/'manifest.json','2325f28cc6f45e6c8b1191902b5e3370a3c7bbd3a7935eee5c1b551a3ab417bc')
    assert st['source'] == SOURCE and st['actualExit'] == 0 and st['sourceHashes'] == changed
    for label in ('pmd','checkstyle'):
        raw = (sp/(label+'.xml')).read_bytes();assert data.sha(raw) == st['reports'][label]['sha256'] and st['reports'][label]['findings'] == st['reports'][label]['processingErrors'] == 0
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    removed = {r['id'] for r in original if r['path'] in changed}
    assert removed == {'PMD-05808','PMD-06923','PMD-06924','PMD-06925','PMD-06926'} and removed <= ids and not removed & (refs|pending)
    assert set(delta['removedFindingIds']) == removed and not delta['freshRows'] and not delta['addedFindingIds']
    assert all(r['rule']=='AvoidDuplicateLiterals' and r['inputSha256'] == previous['begin']['inputHashes'][r['path']] for r in original if r['id'] in removed)
    ids -= removed;assert [len(ids),len(refs),len(pending)] == [8541,3181,766] and len({r['id'] for r in original}-ids) == 876 and len([i for i in ids if i.startswith('PMD-NEW-')]) == 8
    expected = dict(actualExit=0,source=SOURCE,changedSourcePaths=2,sourceDerivedRaw=8541,totalPriorCorrections=876,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=5,joinedContextWarnings=3181,sourceReboundCurrentWholePending=766,actualViolationCount=None,wholeF03Accepted=False,newAccepted=0,productTestsExecuted=0)
    require(m,expected);negatives = 0
    for key,wrong in [('source','0'*40),('sourceDerivedRaw',8546),('totalPriorCorrections',871),('totalIntroducedDiagnosticsRetained',0),('joinedContextWarnings',3182),('sourceReboundCurrentWholePending',720),('actualViolationCount',0),('wholeF03Accepted',True)]:
        assert expected[key] != wrong;bad = dict(m);bad[key] = wrong
        try:
            require(bad,expected)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('wrong current seven-removal set accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=PIN,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),unreferenced=len(ids-refs),totalCorrections=876,allIntroducedDiagnosticsRetained=8,metadataNegativeVectors=negatives,sourceCorrections=5,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
