"""Read public saved Test sources and current token preservation only; no native/product action."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import original_tokens, tokens

COUNTS=dict(ChildDirectoryPublicationTest=14,ExceptionValueContractTest=1,ExistingFileAccessTest=1,
    FactoryResourceScopeTest=28,LinuxDirectoryCallsTest=1,LinuxExecDescriptorsTest=3,LinuxFileLockTest=2,
    LinuxFilesystemClassifierTest=2,LinuxHostDirectoryCallsTest=1,LinuxInodeSecurityTest=6,
    LinuxProcessExecTest=1,LinuxSealedProofTest=9,LinuxStartupAdmissionTest=4,LinuxStartupFileLockTest=4,
    OwnedDirectoryFactoryTest=2,OwnedTransferDirectoryTest=5,PrivateChildDirectoryTest=7,
    PrivateDirectoryEntryTest=19,ResourceScopeTest=6,ServiceConfigFilesTest=1,StorageAttributeGuardTest=4,
    StorageRootInspectionTest=2)

def main():
    invocation=capture(Path(__file__))
    out=data.BASE/'PG10238-storage-identifier-context-v1'
    assert not out.exists()
    index=data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/manifest.json',
        'f5dafc428c0e2367f79e0e59cd91b125639a88880f7be7bad72e879c0509527c')
    sites=data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected=[r for r in sites if r['expectedAstKind']=='IDENTIFIER' and 'schubert-nk-storage/' in r['path']]
    assert len(selected)==123 and Counter(Path(r['path']).stem for r in selected)==COUNTS
    normal=data.read_checked(data.BASE/'PG10226-header-profile-six-compile-v1/manifest.json',
        'ffb1b71ad14efa4b8921c58a19541728243e35d60f873983528bce177b914b9c')
    old=data.read_checked(data.BASE/'PG10100-query-batch-six-compile-v1/manifest.json',
        'a2a8eb62b574693a47e5ce82b830185a7db3fd41f4af61ba4341b598c5f8e3f3')
    uid=data.read_checked(data.BASE/'PG10136-uid-source-quality-post-v1/manifest.json',
        'f345c162b90a5803d21d8a6e36923562f94768b8cae2eaf93d30eb1ed72eaa29')
    old_root=Path(old['jars']['storage']['path']).parents[3]
    current,rows={},[]
    for r in selected:
        path=r['path']
        before=(old_root/path).read_bytes()
        after=(data.ROOT/path).read_bytes()
        assert data.sha(before)==r['sourceSha256']==old['begin']['inputHashes'][path]
        current[path]=data.sha(after)
        assert current[path]==normal['begin']['inputHashes'][path]
        if Path(path).stem=='LinuxInodeSecurityTest':
            assert current[path]==uid['currentTestSourceSha256'] and uid['originalOracleAndOtherMethodsTokensPreserved']
            assert original_tokens(after.decode())==tokens(before.decode())
        else: assert before==after
        lines=before.decode().splitlines()
        rows.append(dict(r,currentSourceSha256=current[path],historicalLineNotCurrent=True,
            reviewedHistoricalContextSha256=data.sha('\n'.join(lines[max(0,r['line']-15):r['line']+3]).encode()),
            verdict='NO_NEW_DEFECT_IDENTIFIED_IN_CONTEXT_NOT_DYNAMIC_OR_WHOLE_ORACLE_PASS'))
    assert len(current)==22
    record='evidence/01_PT/018_NK-OPS-001/2039_Storage間接期待値123siteレビュー結果.md'
    text=(data.ROOT/record).read_text()
    assert all('|'+n+'|' in text for n in COUNTS)
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        reviewedSites=123,sourceFiles=22,currentSourceHashes=current,counts=COUNTS,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),humanReviewRecord=record,
        humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),uidPreservationProofSha256='f345c162b90a5803d21d8a6e36923562f94768b8cae2eaf93d30eb1ed72eaa29',
        contextReviewOnly=True,automaticIndependenceVerdict=False,newDefectsIdentified=0,
        prior202IdentifierCandidateContextsReviewed=True,constructorCandidatesStillUnreviewed=50,
        targetCodeExecuted=False,productTestsExecuted=0,externalActions=0,newAccepted=0,
        wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))

if __name__=='__main__': main()
