"""Bind the corrected UID oracle and retained static results to its actual source/run."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg10130_uid_oracle_preflight import TEST, BINARY, original_tokens, tokens


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10136-uid-source-quality-post-v1'
    assert not out.exists()
    def read(name, digest):
        return data.read_checked(data.BASE/name/'manifest.json',digest)
    normal = read('PG10128-uid-oracle-six-compile-v1','7738e9ba61b5166e1ca9ed2223f6c7ce494051c9837526df1b2f549a0b7a92be')
    old = read('PG10100-query-batch-six-compile-v1','a2a8eb62b574693a47e5ce82b830185a7db3fd41f4af61ba4341b598c5f8e3f3')
    static = read('PG10127-uid-oracle-precommit-static-v2','e41e9942ef8159c5e790e544ec151d08bc7c89c33b3cd74551529e2156378b32')
    pt = read('PG10135-uid-oracle-post-v2','43685c265a5a73cc4a422ce75a7e52a795841282f2ff291dc16c1e7f70f2928d')
    pre = read('PG10130-uid-oracle-preflight-v1','903994e5c0089cb146aa5beafc107ae6a990b76812866212420aa35f8402354e')
    assert normal['source'] == pt['source'] == pre['source'] == 'd17f122d2026b804be626bf7a3b76912923bd240'
    assert normal['actualExit'] == pt['actualExit'] == pre['actualExit'] == normal['testsExecuted'] == 0
    hashes, previous = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(previous)
    assert {p:h for p,h in hashes.items() if h != previous[p]} == static['sourceHashes']
    assert set(static['sourceHashes']) == {TEST}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    text = (data.ROOT/TEST).read_text()
    old_root = Path(old['jars']['storage']['path']).parents[3]
    assert original_tokens(text) == tokens((old_root/TEST).read_text())
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 2 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    pmd = data.BASE/'PG10127-uid-oracle-precommit-static-v2/pmd.xml'
    assert data.sha(pmd.read_bytes()) == static['reports']['pmd']['sha256']
    findings = []
    for file in ET.parse(pmd).getroot().iter():
        if file.tag.rsplit('}',1)[-1] != 'file':
            continue
        assert str(Path(file.get('name')).relative_to(data.ROOT)) == TEST
        for v in file:
            line = int(v.get('beginline'))
            assert v.get('rule') == 'DoNotUseThreads' and line in (267,283)
            findings.append(dict(rule=v.get('rule'),line=line,status='NON_APPLICABLE_JAVAEE_CONTEXT',
                reason='standalone method-owned bounded executor/TWR/futures, not managed JavaEE; this method was NOT executed here'))
    assert len(findings) == 2
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before, after = test_classes(old),test_classes(normal)
    selected = ('storage',BINARY.replace('.','/')+'.class')
    assert set(before) == set(after) and len(after) == 1931
    changed = [k for k in after if after[k] != before[k]]
    assert changed == [selected]
    assert pt['tests'] == pt['suites'] == 1 and pt['newTestIds'] == 0 and pt['forbiddenProductProbeHits'] == 0
    assert pt['ownedTemporaryAfterEmpty'] and pt['onlyOneTestAndNoOtherNativeMethodsExecuted']
    assert not pt['coverageUnion'] and not pt['nativeCohortQualified'] and not pt['targetUnitsFour100']
    assert pre['literalMetadataVectors'] == 3
    verify(invocation)
    out.mkdir()
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        correctedExistingTestId='PT-DB-INBOX-125',currentSourceTests=1,newTestIds=0,
        currentTestSourceSha256=hashes[TEST],originalOracleAndOtherMethodsTokensPreserved=True,
        mainClassesByteIdentical=1843,physicalTestClasses=1931,otherTestClassesByteIdentical=1930,
        changedTestClass=dict(module=selected[0],name=selected[1],before=before[selected],after=after[selected]),
        rawStaticExit=1,rawPmdFindings=2,checkstyleFindings=0,individualApplicability=findings,
        suppressionsAdded=False,literalMetadataVectors=3,currentJavaPaths=1803,currentMainPaths=965,currentTestPaths=838,
        units=pt['units'],historical52TestSuccessTransferred=False,productTestsReexecuted=0,
        externalActions=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,mainUnchanged=1843,otherTestClassesByteIdentical=1930,
        tests=1,newTestIds=0,manifestSha256=data.sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
