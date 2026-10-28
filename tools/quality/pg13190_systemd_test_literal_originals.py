"""Preserve one exact original Test and 40 diagnostics before PG-only constant extraction."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

PATH = 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSessionTest.java'
OLD_SHA = 'a3cef94ea182a9764cb6ee1f97ba7315d2b3cbaebdde5c7d7d42c7a4f7891037'
OUT = data.BASE/'PG13190-systemd-test-literal-originals-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13176-numeric-ceiling-six-compile-v1/manifest.json','ba6cbaa31b2d244115de5665d30142d3b067da21625a01af415b1f002fbe940f')
    raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes()
    rows = [r for r in json.loads(raw) if r['path'] == PATH]
    text = (data.ROOT/PATH).read_bytes();assert data.sha(text) == normal['begin']['inputHashes'][PATH] == OLD_SHA
    assert len(rows) == 40 and {r['inputSha256'] for r in rows} == {OLD_SHA}
    removed = [r['id'] for r in rows if r['attributes']['rule'] == 'AvoidDuplicateLiterals'];assert len(removed) == 21
    verify(invocation);OUT.mkdir()
    data.write(OUT/'original.json',dict(path=PATH,sha256=OLD_SHA,text=text.decode(),findings=rows,originalFindingsSha256=data.sha(raw)))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,originalSha256=data.sha((OUT/'original.json').read_bytes()),removedFindingIds=removed,retainedRaw=19,productTestsExecuted=0,newAccepted=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
