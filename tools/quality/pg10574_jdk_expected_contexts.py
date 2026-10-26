"""Unchanged expected-expression contexts only; no consumer compilation or execution."""
from collections import Counter
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument

SOURCE = 'c91916e8fe1d46768b4ffcd8607164e973aa1bde'
OUT = data.BASE/'PG10574-jdk-expected-contexts-v1'
TYPES = {'UUID':'java.util.UUID','HashSet':'java.util.HashSet','TreeSet':'java.util.TreeSet',
    'String':'java.lang.String','java.math.BigInteger':'java.math.BigInteger',
    'BigInteger':'java.math.BigInteger','ArrayList':'java.util.ArrayList'}
PRIORS = {
    'PG10330-wire-helper-context-v1':'3adecef2effbdf4d4940ff60e130491f08de3db773f677ec0d1acf0bdd46021d',
    'PG10362-golden-helper-context-v1':'5082a9445528742cda2184924d73aae9cab2dbc7475fd73a1a314fc62362c6c6',
    'PG10364-byte-response-helper-context-v1':'76b4e4560b6070bb477b04dbf48d603781ef9c2dc6a4ea9acf7c1204f43dcfa2'}


def key(row):
    return tuple(row[name] for name in ('path','method','line','expectedExpressionSha256'))


def jdk_binding(text,name):
    if re.search(r'\b(?:class|record|interface|enum)\s+'+re.escape(name)+r'\b',text):
        raise ValueError('shadow type is not a reviewed JDK value')
    if '.' not in name and name != 'String' and 'import '+TYPES[name]+';' not in text:
        raise ValueError('exact JDK import required')
    if name == 'String' and re.search(r'\bimport\s+(?!java\.lang\.)[\w.]+\.String;',text):
        raise ValueError('java.lang.String must not be shadowed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    origin = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    rows = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',origin['sitesJsonSha256'])
    carrier = data.read_checked(data.BASE/'PG10520-constructor-carrier-review-v3/manifest.json',
        'de115abc7337ea95939b3fc80360882f250b5d3b977596b179c815a6590afa23')
    done = {key(r) for r in data.read_checked(data.BASE/'PG10520-constructor-carrier-review-v3/sites.json',carrier['sitesSha256'])}
    previous = {}
    for label,pin in PRIORS.items():
        prior = data.read_checked(data.BASE/label/'manifest.json',pin)
        for row in data.read_checked(data.BASE/label/'reviewed-sites.json',prior['reviewedSitesSha256']):
            previous.setdefault(key(row),[]).append(label)
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    selected = []
    for row in rows:
        types = set(row['expectedConstructorTypes'])
        if not types or not types <= set(TYPES) or key(row) in done:
            continue
        text = (data.ROOT/row['path']).read_text()
        if data.sha(text.encode()) != row['sourceSha256']:
            continue
        assert row['sourceSha256'] == normal['begin']['inputHashes'][row['path']]
        for name in types:
            jdk_binding(text,name)
        expression = first_argument(text,row)
        start,end = expression[0][1],expression[-1][2]
        assert data.sha(text[start:end].encode()) == row['expectedExpressionSha256']
        reused = previous.get(key(row),[])
        relation = Path(row['path']).stem == 'LogQueryApplicationServiceTest' and row['method'] == 'brokerBody'
        category = ('PRIOR_STATIC_CONTEXT_REFERENCE_NOT_NEW' if reused else
            'OUTPUT_METADATA_RELATION_NOT_INDEPENDENT_COMPLETE_GOLDEN' if relation else
            'JDK_VALUE_FIXED_INPUT_OR_COLLECTION_CONTEXT_REVIEW_ONLY')
        selected.append(dict(row,jdkTypeBindings={name:TYPES[name] for name in sorted(types)},
            priorContextReferences=reused,contextReviewCategory=category))
    counts = Counter(r['contextReviewCategory'] for r in selected)
    assert len(selected) == 104 and len({r['path'] for r in selected}) == 33
    assert counts == dict(PRIOR_STATIC_CONTEXT_REFERENCE_NOT_NEW=38,
        OUTPUT_METADATA_RELATION_NOT_INDEPENDENT_COMPLETE_GOLDEN=2,
        JDK_VALUE_FIXED_INPUT_OR_COLLECTION_CONTEXT_REVIEW_ONLY=64)
    companions = [
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/LoginReplayServiceTest.java',
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionServiceTest.java',
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserApplicationFixture.java',
        'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BackupStepFixture.java',
        'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/CleanupStepFixture.java',
        'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java',
        'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionAttributeCodecTest.java',
        'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt']
    companion_hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in companions}
    assert all(normal['begin']['inputHashes'][p] == h for p,h in companion_hashes.items())
    rejected = 0
    for sample,name in (('import other.UUID;','UUID'),('class UUID {}','UUID'),('import other.String;','String')):
        try:
            jdk_binding(sample,name)
        except ValueError:
            rejected += 1
    assert rejected == 3
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'reviewed-sites.json',selected)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sites=104,consumerSources=33,reviewedSitesSha256=data.sha((OUT/'reviewed-sites.json').read_bytes()),
        counts=dict(counts),sourceHashes={r['path']:r['sourceSha256'] for r in selected},
        companionHashes=companion_hashes,metadataNegativeVectors=3,
        currentChangedWebTraceHandledSeparately='PG10564/2084_NOT_REPLAYED_OR_OLD_HASH_REBOUND',
        priorContextReferencesNotRuntimeTransfers=True,automaticIndependenceVerdict=False,
        wholeCaseFixtureCorrectnessAccepted=False,newDefectsIdentified=0,
        productTestsExecuted=0,targetCompilation=0,targetClassLoading=0,externalActions=0,
        newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
