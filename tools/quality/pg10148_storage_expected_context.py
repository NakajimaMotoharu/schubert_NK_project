"""Bind 114 human-reviewed source sites; old UID line origin is explicit, not silently relabelled."""
from collections import Counter
from pathlib import Path
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

COUNTS = dict(ChildDirectoryPublicationTest=3,ExistingFileAccessTest=1,FactoryResourceScopeTest=7,
    LinuxDirectoryCallsTest=1,LinuxExecDescriptorsTest=6,LinuxFileLockTest=19,LinuxFilesystemClassifierTest=1,
    LinuxHostDirectoryCallsTest=4,LinuxInodeSecurityTest=7,LinuxProcessExecTest=7,LinuxSealedProofTest=4,
    LinuxStartupAdmissionTest=18,LinuxStartupFileLockTest=10,OwnedTransferDirectoryTest=1,
    PrivateChildDirectoryTest=9,ResourceScopeTest=2,ServiceConfigFilesTest=1,ServiceCredentialIdTest=4,
    ServiceCredentialLocationTest=2,StorageAttributeGuardTest=1,EnumValueCatalogCompatibilityTest=6)


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10148-storage-expected-context-v1'
    assert not out.exists()
    index = data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/manifest.json',
        'f5dafc428c0e2367f79e0e59cd91b125639a88880f7be7bad72e879c0509527c')
    rows = data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected = [r for r in rows if 'schubert-nk-storage/' in r['path'] and r['expectedMethodSelectors'] and not r['sharedDirectMethodSelectors']]
    assert len(selected) == 114 and Counter(Path(r['path']).stem for r in selected) == COUNTS
    uid = 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/LinuxInodeSecurityTest.java'
    current = {r['path']:data.sha((data.ROOT/r['path']).read_bytes()) for r in selected}
    assert len(current) == 21 and {p for p,h in current.items() if h != index['sourceHashes'][p]} == {uid}
    proof = data.read_checked(data.BASE/'PG10136-uid-source-quality-post-v1/manifest.json',
        'f345c162b90a5803d21d8a6e36923562f94768b8cae2eaf93d30eb1ed72eaa29')
    assert proof['originalOracleAndOtherMethodsTokensPreserved'] and proof['currentTestSourceSha256'] == current[uid]
    protocol = data.read_checked(data.BASE/'PG10146-protocol-expected-context-v1/manifest.json',
        '739f22ba2d61ab18b668870d4dcacba8b4d349e1a967c0693377886265f41c36')
    assert protocol['reviewedSites'] == 95 and protocol['productTestsExecuted'] == 0
    flaw = [r for r in selected if Path(r['path']).stem == 'ServiceCredentialLocationTest' and r['line'] == 70]
    assert len(flaw) == 1 and flaw[0]['expectedMethodSelectors'] == ['value.directory']
    record = 'evidence/01_PT/018_NK-OPS-001/2031_Storage直接期待値114site文脈レビュー結果.md'
    text = (data.ROOT/record).read_text()
    assert all('|'+n+'|' in text for n in COUNTS)
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',selected)
    data.write(out/'manifest.json',dict(actualExit=0,source='d17f122d2026b804be626bf7a3b76912923bd240',invocation=invocation,
        reviewedSites=114,counts=COUNTS,sourceHashes=current,lineOriginSource=index['source'],
        uidCurrentBindingProof='f345c162b90a5803d21d8a6e36923562f94768b8cae2eaf93d30eb1ed72eaa29',
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),humanReviewRecord=record,
        humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),contextReviewOnly=True,
        noSameProductionExpectedDefectForReviewedContext=113,oracleFixRequired=1,issue='BUG-1798',horizontalIssue='YKT-1549',
        protocolReviewedSites=95,priorSameSelectorReviewed=7,direct216ContextReviewedNotGatePass=True,
        remainingDirectExpectedContextSites=0,unresolvedIdentifierSites=202,countsOverlapNotCompletionRate=True,
        productTestsExecuted=0,externalActions=0,newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,reviewedSites=114,fixRequired=1,
        manifestSha256=data.sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
