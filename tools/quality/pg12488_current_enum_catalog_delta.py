"""Exact five current enum catalog Test corrections; retain all previous raw reasons and added diagnostics."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12462_current_config_template_delta import state as before_config

SOURCE = '6929166ee735effb5cae211e1f4cfe44f0b97a0a'
OUT = data.BASE/'PG12488-current-enum-catalog-delta-v1'

def state():
    ids,refs,pending=before_config()
    p=data.BASE/'PG12462-current-config-template-delta-v1/manifest.json'
    m=data.read_checked(p,'2236248507325db831cd9af306660cdb5f251f21683118b9c80b72ac3d780b0f')
    d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    removed=set(d['removedFindingIds'])
    assert removed=={f'PMD-{n:05}' for n in range(5240,5247)} and not d['freshRows'] and not d['addedFindingIds']
    ids-=removed
    assert [len(ids),len(refs),len(pending)]==[8546,3181,766]
    return ids,refs,pending

def main():
    invocation = capture(__file__);assert not OUT.exists();ids,refs,pending = state()
    normal = data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe')
    previous = data.read_checked(data.BASE/'PG12450-config-template-six-compile-v1/manifest.json','face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    changed = {p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p] != h}
    assert set(changed) == {'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/EnumValueCatalogCompatibilityTest.java','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/EnumValueCatalogCompatibilityTest.java'}
    sp = data.BASE/'PG12480-enum-catalog-static-v1';st = data.read_checked(sp/'manifest.json','2325f28cc6f45e6c8b1191902b5e3370a3c7bbd3a7935eee5c1b551a3ab417bc')
    assert st['actualExit'] == 0 and st['source'] == SOURCE and st['sourceHashes'] == changed
    for label in ('pmd','checkstyle'):
        raw = (sp/(label+'.xml')).read_bytes();assert data.sha(raw) == st['reports'][label]['sha256']
        assert st['reports'][label]['findings'] == st['reports'][label]['processingErrors'] == 0
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    removed = {r['id'] for r in original if r['path'] in changed}
    assert removed == {'PMD-05808',*{f'PMD-{n:05}' for n in range(6923,6927)}} and removed <= ids and not removed & (refs|pending)
    assert all(r['rule']=='AvoidDuplicateLiterals' and r['inputSha256'] == previous['begin']['inputHashes'][r['path']] for r in original if r['id'] in removed)
    ids -= removed;assert len(ids) == 8541 and len({r['id'] for r in original}-ids) == 876 and len([i for i in ids if i.startswith('PMD-NEW-')]) == 8
    verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=[],removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=5,oldScopeFindings=5,newScopeFindings=0,replacedContextWarnings=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),changedSourcePaths=2,sourceDerivedRaw=8541,mainRaw=1512,testRaw=7029,totalPriorCorrections=876,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=5,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
