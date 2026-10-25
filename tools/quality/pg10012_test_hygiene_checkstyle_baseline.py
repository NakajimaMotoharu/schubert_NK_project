"""Fresh public Test-source Checkstyle diagnosis; exact three held sources remain untouched."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as stage

SOURCE = 'bba24d15923831a17e5464328b70fdb950fb2fcf'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10012-test-hygiene-checkstyle-baseline-v1'
OUT = data.BASE/'PG10012-test-hygiene-checkstyle-baseline-v1'
HELD = {
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/error/TemporaryFailureGraph329Test.java',
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/error/ApiStartupGraph330Test.java',
    'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebStartupGraph330Test.java'}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    tests = {p:h for p,h in hashes.items() if '/src/test/java/' in p and p.endswith('.java')}
    assert len(tests) == 835 and HELD <= set(tests)
    selected = {p:h for p,h in tests.items() if p not in HELD}
    assert len(selected) == 832
    static = stage.TC/'static-gates-20261015'
    jar = static/'checkstyle-14.3.0-all.jar'
    rule = data.ROOT/'tools/quality/static/checkstyle.xml'
    tool_hashes = {str(p):data.sha(p.read_bytes()) for p in (jar,rule)}
    SLOT.mkdir(mode=0o700)
    listing = SLOT/'test-sources.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(data.ROOT/p)+'\n' for p in sorted(selected)))
    result = stage.step('checkstyle',[str(stage.TC/'jdk-25.0.4/bin/java'),'-jar',str(jar),
        '-c',str(rule),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT)
    document = ET.parse(SLOT/'checkstyle.xml').getroot()
    errors = [n.attrib for n in document.findall('.//error')]
    assert not result['timedOut']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in tool_hashes.items())
    verify(invocation)
    OUT.mkdir()
    (OUT/'checkstyle.xml').write_bytes((SLOT/'checkstyle.xml').read_bytes())
    value = dict(actualExit=0,qualification='DIAGNOSTIC_COMPLETED_NOT_QUALITY_PASS',source=SOURCE,invocation=invocation,
        stage=result,rawCheckstyleExit=result['actualExit'],rawCheckstyleFindings=len(errors),
        ruleCounts=dict(Counter(r['source'] for r in errors)),selectedSourceHashes=selected,
        heldSourceHashes={p:tests[p] for p in sorted(HELD)},toolAndRuleHashes=tool_hashes,
        reportSha256=data.sha((OUT/'checkstyle.xml').read_bytes()),mainModified=False,testModified=False,
        productTestsExecuted=0,externalActions=0,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawCheckstyleExit=result['actualExit'],findings=len(errors),rules=value['ruleCounts'],
        selected=832,held=3,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
