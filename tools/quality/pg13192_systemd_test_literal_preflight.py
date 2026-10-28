"""Static PG-only Test extraction: full inverse and exactly 21 original removals, no Test run."""
from collections import Counter
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13190_systemd_test_literal_originals import PATH, OLD_SHA
from pg13191_systemd_test_literal_inverse import inverse, negative, CONSTANTS
from pg13132_main_literal_preflight import signature
import pg9666_pagination_static as runner

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13192-systemd-test-literal-preflight-v1'
OUT = data.BASE/'PG13192-systemd-test-literal-preflight-v1'

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    om = data.read_checked(data.BASE/'PG13190-systemd-test-literal-originals-v1/manifest.json','9159076b27e5b090f8aa550402456d51d90daeb5790d84836fe74f113309457b')
    original = data.read_checked(data.BASE/'PG13190-systemd-test-literal-originals-v1/original.json',om['originalSha256'])
    assert data.sha(original['text'].encode()) == OLD_SHA
    old = data.read_checked(data.BASE/'PG13176-numeric-ceiling-six-compile-v1/manifest.json','ba6cbaa31b2d244115de5665d30142d3b067da21625a01af415b1f002fbe940f')
    current = (data.ROOT/PATH).read_text();inverse_proof = inverse(original['text'],current);vectors = negative(original['text'],current)
    hashes = {PATH:data.sha(current.encode())}
    assert {p for p,sha in old['begin']['inputHashes'].items() if data.sha((data.ROOT/p).read_bytes()) != sha} == {PATH}
    expected = Counter(signature(r['attributes'],r['message']) for r in original['findings'] if r['id'] not in om['removedFindingIds']);assert sum(expected.values()) == 19
    assert set(CONSTANTS.values()) == {r['message'].split('"')[1] for r in original['findings'] if r['id'] in om['removedFindingIds']}
    static = runner.TC/'static-gates-20261015';rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    snapshot = Path(old['jars']['bootstrap']['path']).parents[3]
    cp = (snapshot/'src/schubert-nk-bootstrap/target/pgpt-test-classpath.txt').read_text().strip()
    deps = {p:data.sha(Path(p).read_bytes()) for p in cp.split(os.pathsep)}
    SLOT.mkdir();runner.SLOT = SLOT;listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:stream.write(str(data.ROOT/PATH)+'\n')
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT),
        'checkstyle':runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT),
    }
    actual = Counter();rows = [];root = ET.parse(SLOT/'pmd.xml').getroot()
    assert not [x for x in root.iter() if x.tag.rpartition('}')[2] in ['error','configerror']]
    for file in root:
        if file.tag.rpartition('}')[2] != 'file':continue
        assert file.get('name') == str(data.ROOT/PATH)
        for node in file:
            assert node.tag.rpartition('}')[2] == 'violation'
            actual[signature(dict(node.attrib),node.text.strip())] += 1
            rows.append(dict(path=PATH,attributes=dict(node.attrib),message=node.text.strip()))
    assert actual == expected
    assert not [x for x in ET.parse(SLOT/'checkstyle.xml').getroot().iter() if x.tag == 'error']
    assert stages['pmd']['actualExit'] == 4 and stages['checkstyle']['actualExit'] == 0 and not any(x['timedOut'] for x in stages.values())
    assert data.sha((data.ROOT/PATH).read_bytes()) == hashes[PATH]
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tools,**deps}.items())
    verify(invocation);OUT.mkdir()
    for name in stages:
        with (OUT/(name+'.xml')).open('xb') as stream:stream.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,baseSource=old['source'],invocation=invocation,
        candidateSourceHashes=hashes,originalTokenInverse=inverse_proof,negativeVectors=vectors,
        removedFindingIds=om['removedFindingIds'],retainedRawFindings=rows,rawStatic=19,rawStaticGateExit=1,
        stages=stages,toolAndRuleHashes=tools,dependencyHashes=deps,
        reports={name:data.sha((OUT/(name+'.xml')).read_bytes()) for name in stages},
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
