"""Independent static delta for one UUID fixture; nine pre-existing literals remain explicit."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10690_current_global_static_post import finding_rows

OUT = data.BASE/'PG10749-protocol-locale-static-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    static_path = data.BASE/'PG10744-protocol-uppercase-static-v1/manifest.json'
    static = data.read_checked(static_path,'35037cfaebc6176d4cd288337518e278e80ec6d3ac660727e660d6e64645b602')
    global_path = data.BASE/'PG10690-current-global-static-post-v1/manifest.json'
    global_meta = data.read_checked(global_path,'465c7c64bc75923d275436c72656ddc5b537f2c15982a71a0b4681a19ef03627')
    prior = data.read_checked(global_path.parent/'findings.json',global_meta['findingsSha256'])
    path, = static['sourceHashes']
    assert path.endswith('/SemanticFieldValueTest.java')
    assert data.sha((data.ROOT/path).read_bytes()) == static['sourceHashes'][path]
    old = [r for r in prior if r['path'] == path and r['scanner'] == 'pmd']
    assert len(old) == 10 and sum(r['rule'] == 'UseLocaleWithCaseConversions' for r in old) == 1
    retained = [r for r in old if r['rule'] != 'UseLocaleWithCaseConversions']
    raw = (static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw) == static['reports']['pmd']['sha256']
    current,_ = finding_rows(raw,'pmd',static['sourceHashes'])
    assert len(current) == len(retained) == static['reports']['pmd']['findings'] == 9
    for before,after in zip(retained,current):
        assert before['rule'] == after['rule'] == 'AvoidDuplicateLiterals'
        expected = dict(before['attributes'])
        for key in ('beginline','endline'):
            expected[key] = str(int(expected[key])+1)
        assert expected == after['attributes']
        assert re.sub(r'first occurrence is on line (\d+)',lambda m:'first occurrence is on line '+str(int(m[1])+1),before['message']) == after['message']
    cs = (static_path.parent/'checkstyle.xml').read_bytes()
    assert data.sha(cs) == static['reports']['checkstyle']['sha256']
    parsed,_ = finding_rows(cs,'checkstyle',static['sourceHashes'])
    assert not parsed and static['reports']['checkstyle']['findings'] == 0
    assert static['actualExit'] == 1 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=static['source'],invocation=invocation,
        staticManifestSha256=data.sha(static_path.read_bytes()),originalIndexManifestSha256=data.sha(global_path.read_bytes()),
        localeRuleRemoved=1,remainingRawPmdFindings=9,remainingRule='AvoidDuplicateLiterals',rawStaticExit=1,
        originalOtherFindingAttributesPreserved=True,checkstyleFindings=0,productTestsExecuted=0,
        coverage=None,externalActions=0,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
