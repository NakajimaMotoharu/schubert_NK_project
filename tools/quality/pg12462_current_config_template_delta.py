"""Exact seven current Test corrections; retain all previous raw reasons and added diagnostics."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg12436_current_resource_compound_delta import state as before_compound

SOURCE = 'd6c01d3aed6bd1b546b6f5989fe80705e6e1262f'
OUT = data.BASE/'PG12462-current-config-template-delta-v1'

def state():
    ids,refs,pending = before_compound()
    p = data.BASE/'PG12436-current-resource-compound-delta-v1/manifest.json'
    m = data.read_checked(p,'dd6bab9f8cbb6ba1d1bf6a031f0d194e3c61cb60f02017a4dc5bdd56060573f0')
    d = data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    assert not d['removedFindingIds'] and not d['addedFindingIds']
    reviewed = {r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
    assert len(reviewed) == 46;refs |= reviewed;pending |= reviewed
    assert [len(ids),len(refs),len(pending)] == [8553,3181,766]
    return ids,refs,pending

def main():
    invocation = capture(__file__);assert not OUT.exists();ids,refs,pending = state()
    normal = data.read_checked(data.BASE/'PG12450-config-template-six-compile-v1/manifest.json','face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2')
    previous = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    changed = {p:h for p,h in hashes.items() if previous['begin']['inputHashes'][p] != h}
    assert list(changed) == ['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java']
    sp = data.BASE/'PG12454-config-template-static-v1';st = data.read_checked(sp/'manifest.json','91308d49aaeea62224bdfb75eafcec99a62e6ea5ff7daa35dc8d0bf4e7f2c3bb')
    assert st['actualExit'] == 0 and st['source'] == SOURCE and st['sourceHashes'] == changed
    for label in ('pmd','checkstyle'):
        raw = (sp/(label+'.xml')).read_bytes();assert data.sha(raw) == st['reports'][label]['sha256']
        assert st['reports'][label]['findings'] == st['reports'][label]['processingErrors'] == 0
        assert not [n for n in ET.fromstring(raw).iter() if n.tag.rpartition('}')[2] in ('violation','error','configerror')]
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    removed = {r['id'] for r in original if r['path'] in changed}
    assert removed == {f'PMD-{n:05}' for n in range(5240,5247)} and removed <= ids and not removed & (refs|pending)
    assert all(r['rule'] in ('AvoidDuplicateLiterals','AvoidFieldNameMatchingMethodName') and r['inputSha256'] == previous['begin']['inputHashes'][r['path']] for r in original if r['id'] in removed)
    ids -= removed;assert len(ids) == 8546 and len({r['id'] for r in original}-ids) == 871 and len([i for i in ids if i.startswith('PMD-NEW-')]) == 8
    verify(invocation);OUT.mkdir();data.write(OUT/'delta.json',dict(source=SOURCE,sourceInputDelta=changed,freshRows=[],removedFindingIds=sorted(removed),addedFindingIds=[],originalScopeFindings=7,oldScopeFindings=7,newScopeFindings=0,replacedContextWarnings=0,newProductExecutions=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),changedSourcePaths=1,sourceDerivedRaw=8546,mainRaw=1512,testRaw=7034,totalPriorCorrections=871,totalIntroducedDiagnosticsRetained=8,sourceScopeCorrectionsAlreadyCounted=7,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),actualViolationCount=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
