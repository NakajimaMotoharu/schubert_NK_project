"""Program002 new three/old five binding, independent scope dimensions, no PT replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from quality_scope_dimensions import bind

OUT = data.BASE/'PG13168-nfc-golden-completion-v1'
SOURCE = 'b11fe71bd20e244dd10c83bd339f8345a0c1f085'
DOCUMENTS = [
    'evidence/01_PT/018_NK-OPS-001/2422_FieldCodec_NFC固定scalar・wire_単体テスト仕様.md',
    'evidence/01_PT/018_NK-OPS-001/2423_FieldCodec_NFC固定scalar・wire_実行結果.md',
    'evidence/01_PT/002_NK-PRO-002/001_NK-PRO-002_単体テスト仕様書.md',
    'evidence/01_PT/002_NK-PRO-002/002_NK-PRO-002_実行結果.md',
]

def main():
    invocation = capture(__file__);assert not OUT.exists()
    p = data.read_checked(data.BASE/'PG13164-nfc-golden-post-v2/manifest.json','cdec2827b883dd6e6d75a9aecbe1fbc11f3d42ab36f7bccbfb6a6e9479d275ad')
    plan = data.read_checked(data.BASE/'PG13154-nfc-golden-plan-v1/manifest.json','7695d1297c842faf24096b623194ff74903b849d58f2b4355f002ae9b5a5748f')
    h = data.read_checked(data.BASE/'PG13158-nfc-golden-host-v1/manifest.json','90af523f25fd27284d2fc5de6e2205ab1bfe0fcb4f77db7ae94f0d7e142fcabd')
    t = data.read_checked(data.BASE/'PG13167-nfc-golden-trace-post-v1/manifest.json','da3d04b1e05fac1c49115c75b09140834b4dae8f5bed5e934d261a70cc635a71')
    assert p['source'] == plan['source'] == h['source'] == t['source'] == SOURCE and t['actualExit'] == 0
    dimensions = bind(plan,h,p);assert dimensions.public() == p['dimensions']
    assert dimensions.observed_cases == 8 and dimensions.new_test_ids == 3 and dimensions.suites == 2 and not p['selectedMainCoverage100']
    assert p['rawStatic'] == p['staticGateExit'] == p['spotbugsSixExit'] == 0 and t['wholeWbsAudit']['actualExit'] == 1 and not t['wholeWbsAudit']['passed']
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in h['begin']['sourceInputHashes'].items())
    parent = data.ROOT/'evidence/01_PT/002_NK-PRO-002/evidence';target = parent/'nfc-scalar-goldens'
    assert parent.is_dir() and not parent.is_symlink() and not target.exists()
    new_cases = [r for r in plan['cases'] if r['path'].endswith('/FieldCodecNfcGoldenTest.java')];assert len(new_cases) == 3
    bindings = dict(zip(['PT-CODEC-NFCGOLD001','PT-CODEC-NFCGOLD002','PT-CODEC-NFCGOLD003'],new_cases,strict=True))
    item = dict(actualExit=0,source=SOURCE,primaryWbs='WBS-P002-01',cases=plan['cases'],newTestIdBindings=bindings,
        observedOwnTests=8,suites=2,newUniqueTestIds=3,existingRelatedMethodIds=[r['className']+'#'+r['method'] for r in plan['cases'] if r not in new_cases],
        sessionId=h['sessionId'],oldExecUnion=False,dimensions=dimensions.public(),selectedMain=p['selectedMain'],selectedMainCoverage100=False,wholeArtifactCoverage100=False,
        proofManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13164-nfc-golden-post-v2/manifest.json',proofManifestSha256='cdec2827b883dd6e6d75a9aecbe1fbc11f3d42ab36f7bccbfb6a6e9479d275ad',
        documentHashes={path:data.sha((data.ROOT/path).read_bytes()) for path in DOCUMENTS},
        relatedRd=['MQ-018','MQ-031','MQ-033','MSG-002','MSG-007','MSG-010'],relatedUi=['232§4'],relatedSs=['322§4.1','322§6.1','322§11'],
        relatedBugs=['BUG-2034'],relatedYkt=['YKT-1782'],rawStatic=0,spotbugsSixExit=0,newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None)
    verify(invocation);target.mkdir();data.write(target/'manifest.json',item);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,programIndex=str((target/'manifest.json').relative_to(data.ROOT)),
        programIndexSha256=data.sha((target/'manifest.json').read_bytes()),observedTests=8,suites=2,newUniqueTestIds=3,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
