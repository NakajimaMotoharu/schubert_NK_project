"""Source-level stale oracle proof, not a product execution or measured PT failure."""
import json
import re
import subprocess
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG12402-batch-runtime-oracle-discrepancy-v1'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/bootstrap/BatchRuntimeDependencyTest.java'
POM = 'src/schubert-nk-batch/pom.xml'
OLD = {'dev.codex.schubert:schubert-nk-storage','dev.codex.schubert:schubert-nk-bootstrap','org.flywaydb:flyway-core','org.flywaydb:flyway-database-postgresql','org.postgresql:postgresql','org.apache.artemis:artemis-jakarta-client','org.jspecify:jspecify','com.github.spotbugs:spotbugs-annotations'}
APPROVED = {'io.micrometer:micrometer-core','io.micrometer:micrometer-registry-prometheus'}

def main():
    invocation = capture(__file__);assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json','27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75')
    snapshot = Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    test = (snapshot/TEST).read_text();pom = (snapshot/POM).read_text()
    assert normal['source'] == '14198cb1878ec73319511ba1067133992d335e63' and normal['actualExit'] == normal['testsExecuted'] == 0
    for p in (TEST,POM):
        assert data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == normal['begin']['inputHashes'][p]
    match = re.search(r'assertEquals\(\s*java\.util\.Set\.of\((.*?)\),\s*direct\);',test,re.S)
    assert match is not None
    expected = set(re.findall(r'"([^"\n]+)"',match[1]));assert expected == OLD
    declared = set()
    for block in re.findall(r'<dependency>(.*?)</dependency>',pom,re.S):
        if '<scope>test</scope>' in block:
            continue
        group = re.search(r'<groupId>([^<]+)</groupId>',block)[1]
        artifact = re.search(r'<artifactId>([^<]+)</artifactId>',block)[1]
        declared.add(group+':'+artifact)
    assert declared == OLD|APPROVED and declared-expected == APPROVED and not expected-declared
    ref = subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip()
    assert ref == '8b91944df5820535e23ba2469740f1c0aa94c447'
    authorities = {}
    for p in ['documents/100_RD/170_運用・保守要件/171_運用・監視要件.md','documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md']:
        raw = subprocess.check_output(['git','show',ref+':'+p],cwd=data.ROOT)
        assert 'Micrometer' in raw.decode();authorities[p] = dict(commit=ref,sha256=data.sha(raw))
    decision_path = 'documents/400_PGPT/440_判断/441_実装判断記録.md'
    decision = (data.ROOT/decision_path).read_text()
    part = re.search(r'## PG-D615\b.*?(?=\n## |\Z)',decision,re.S)[0]
    assert 'SDK1.17.1' in part and '公式registry依存だけ追加' in part
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,normalManifestSha256=data.sha((data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json').read_bytes()),testPath=TEST,testSha256=data.sha(test.encode()),pomPath=POM,pomSha256=data.sha(pom.encode()),originalExpectedCoordinates=sorted(expected),independentlyApprovedCoordinates=sorted(OLD|APPROVED),missingFromTest=sorted(APPROVED),unapprovedProductionCoordinates=[],upperAuthorities=authorities,implementationDecision=dict(path=decision_path,id='PG-D615',sectionSha256=data.sha(part.encode())),finding='SOURCE_LEVEL_STALE_TEST_EXPECTATION_NOT_EXECUTED_TEST_FAILURE',productTestsExecuted=0,coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,missingFromTest=sorted(APPROVED),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__':
    main()
