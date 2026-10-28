"""Limited public-receipt result, explicit Program011 index and public-text delta only."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg12706_scenario_writer_public as scan

SOURCE = 'c1d9b6e4b27b236ed8b40724f0701d2a2216237b'
PINS = {
    'PG12950-public-receipt-preflight-v1':'9334d63be060a2dbbfa6a8dc67bedbb4f5e44a0cec136798bd4500c01537797c',
    'PG12951-public-receipt-style-before-v1':'bbebcc762c79c7d8370f2f33b4e9830afcccc3f84eb9954d60b1623ff3b2e383',
    'PG12952-public-receipt-preflight-v2':'4d6ed75f78c3ef5116a7d7a73223f53e6bf33e79e9ddd9b62cf51be83274d128',
    'PG12954-public-receipt-plan-v1':'2f19a802d261701e1cdf4fedc9b7bad4bb0f6c33fa8ebcdbd4066c7ec7e6ca45',
    'PG12956-public-receipt-six-compile-v1':'77e300fe384740d96d4b43accfc0859384c6e65d3fd8cac2da1d55a4ce1e0bf0',
    'PG12958-public-receipt-host-v1':'2b1b13b3484cf1bc4ec6a2a8b1b2c3b15f2156b705e64b75972f1f197e92dc02',
    'PG12960-public-receipt-static-v1':'052425b356a762c807453874a1c2fcd87b9b8997ea0a5d0fec23de7eee909d9b',
    'PG12962-public-receipt-post-v1':'32352ff9472707da5adfcbec67cadd5783a053e61dfce843217da5921e303f99',
    'PG12964-public-receipt-context-v1':'955f91d7d397fc2588f214c6ef3c76abbdae7e7363a4e679159f6a76f4eb80d7',
    'PG12965-public-receipt-context-post-v1':'13f931700724cb8818b347a8e772c389de103d8bda664dd254d98a4b18debe6e',
    'PG12966-public-receipt-trace-v1':'ee2444afbc16b768ae19c6ef19fbcc874ada89f74506d8eb4361e9677da7cb97',
    'PG12967-public-receipt-trace-post-v1':'939dcc0520017586927f94e261975b31707b1bdc82641939389fd7d1e93a9b18'}

def main():
    invocation = capture(__file__)
    out = data.BASE/'PG12968-public-receipt-completion-v1'
    index = data.ROOT/'evidence/01_PT/011_NK-QST-001/evidence/public-receipt-recovery'
    assert not out.exists() and not index.exists()
    for name,digest in PINS.items():
        v = data.read_checked(data.BASE/name/'manifest.json',digest)
        if name in list(PINS)[:3]: assert v['source'] is None and v['baseSource'] == 'e49eb0cc84c62ace468cf389938b23f3e56ba520'
        else: assert v['source'] == SOURCE
        assert v['actualExit'] == (1 if 'static-v1' in name else 0)
    docs = [data.ROOT/'evidence/01_PT/018_NK-OPS-001'/n for n in ['2397_P011公開受付ID生成回復_単体テスト仕様書.md','2398_P011公開受付ID生成回復_実行結果.md']]
    for digest in PINS.values(): assert digest in docs[1].read_text()
    host = data.read_checked(data.BASE/'PG12958-public-receipt-host-v1/manifest.json',PINS['PG12958-public-receipt-host-v1'])
    proof = data.read_checked(data.BASE/'PG12962-public-receipt-post-v1/manifest.json',PINS['PG12962-public-receipt-post-v1'])
    assert host['observedTestExecutions'] == proof['observedTestExecutions'] == 12 and proof['selectedTwoMainCoverage100'] and proof['rawStatic'] == 6
    assert host['publicTraceCheckPassed'] and host['ownedPublicTrace']['length'] == 139
    public = data.BASE/'PG12958-public-receipt-host-v1/PT-QST-RID008.txt'
    assert data.sha(public.read_bytes()) == proof['ownedPublicTrace']['sha256']
    selected = [r for r in host['begin']['cases'] if r['className'].endswith('.QuestionReceiptRecoveryTest')]; assert len(selected) == 4
    verify(invocation); out.mkdir(); index.mkdir()
    data.write(index/'manifest.json',dict(actualExit=0,program='NK-QST-001',source=SOURCE,run=host['sessionId'],invocation=invocation,
        hostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12958-public-receipt-host-v1/manifest.json',hostSha256=PINS['PG12958-public-receipt-host-v1'],
        postManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12962-public-receipt-post-v1/manifest.json',postSha256=PINS['PG12962-public-receipt-post-v1'],
        observedProductTests=12,newUniqueTestIds=4,newTestIdMappings=[dict(testId='PT-QST-RNGREC-'+str(i).zfill(3),className=r['className'],method=r['method'],actual='PASS') for i,r in enumerate(selected,1)],
        publicTraceEvidence=dict(path=str(public.relative_to(data.ROOT)),sha256=data.sha(public.read_bytes()),fixedPublicOnly=True,rawRandomCandidateSaved=False),
        selectedTwoMain=proof['selectedTwoMain'],staticGateExit=1,fullProgramAccepted=False,newAccepted=0,whole451Accepted=False,oldExecUnion=False))
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,manifests=PINS,
        documents={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in docs},programIndexPath=str((index/'manifest.json').relative_to(data.ROOT)),programIndexSha256=data.sha((index/'manifest.json').read_bytes()),
        observedProductTests=12,newBusinessTestIds=4,selectedTwoMainFourCounters100=True,scopeStaticExit=1,
        fullArtifactCoverage100=False,whole451Accepted=False,newAccepted=0,businessExternalActions=0))
    print(json.dumps(dict(completionSha256=data.sha((out/'manifest.json').read_bytes()))))
    scan.OUT = data.BASE/'PG12968-public-receipt-public-v1'; scan.BEFORE = '0f340a345a3fedf530cb970942b258604288f583'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg129','tools/quality/public_receipt_trace_contract.py',
        'tools/quality/architecture/PublicReceiptRecoveryJunitLauncher.java','tools/quality/architecture/PublicReceiptRecoveryArtifactCoverageMeasure.java')
    scan.main()

if __name__ == '__main__': main()
