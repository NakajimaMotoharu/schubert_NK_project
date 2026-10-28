"""Preserve exactly two original Main sources/diagnostics before PG-only constant extraction."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13130-main-literal-originals-v1'
PATHS = {
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/TransferCleanup.java':'ee543c1e7d5981af00d053907114f0ac001b37db912a9e4836edb738f383e41f',
    'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSession.java':'862ef7c72e488db95ebfd9836d92993ea876a4e7a9c472fae0f7c4669f40621c',
}

def main():
    invocation = capture(__file__);assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13106-snapshot-corrected-six-compile-v1/manifest.json','0d052046bbfe7586c491f1cb398566301fae8d958c0e2ae3e660d477961c12c7')
    raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes()
    findings = [r for r in json.loads(raw) if r['id'] in ['PMD-02953','PMD-06175']]
    assert len(findings) == 2 and {r['path']:r['inputSha256'] for r in findings} == PATHS
    originals = []
    for path,sha in PATHS.items():
        value = (data.ROOT/path).read_bytes();assert data.sha(value) == sha == normal['begin']['inputHashes'][path]
        originals.append(dict(path=path,sha256=sha,text=value.decode()))
    verify(invocation);OUT.mkdir();data.write(OUT/'originals.json',dict(source=normal['source'],sources=originals,findings=findings,originalFindingsSha256=data.sha(raw)))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,originalsSha256=data.sha((OUT/'originals.json').read_bytes()),
        originalSources=2,originalFindings=2,productTestsExecuted=0,externalActions=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
