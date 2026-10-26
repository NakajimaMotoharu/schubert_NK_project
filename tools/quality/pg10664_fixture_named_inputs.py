"""Exact fixture definitions and finite controls only; no Test/DB/native/provider execution."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument
from pg10588_record_constructor_review import record_review

OUT = data.BASE/'PG10664-fixture-named-inputs-v1'
DEFINITIONS = {
    'InboxInspectionProgressBoundaryTest':('ONE','high'),
    'AuthSessionRevocationServiceTest':('SESSION',),'AuthSessionServiceTest':('ID',),
    'AuthenticationContextVerifierTest':(), 'BackupArtifactVerifierTest':(), 'MorningBackupRetentionTest':(),
    'ArtemisExpiryPurgeClientTest':('CUTOFF',),'BackupWorkerRequestTest':('RUN','START'),
    'CleanupWorkerRequestTest':('RUN','ACTIVATION','CUTOFF','DIGEST'),
    'CleanupRepositoryTest':('RUN','ZERO'), 'ExpiryAuditRepositoryTest':('RUN','START','END','EXPIRY_CUTOFF'),
    'RunReferenceRepositoryTest':(), 'WebNativeRuntimeOwnedComponentTest':(), 'HttpByteRangeParserTest':('TOTAL',),
}
CONTROLS = {
    'AuthenticationContextVerifierTest':('for (Role role : List.of(Role.USER, Role.ADMIN))',),
    'RunReferenceRepositoryTest':('for (int mask = 0; mask < 8; mask++)','for (boolean consistent : List.of(false, true))',
        'boolean history = (mask & 1) != 0;','boolean inbox = (mask & 2) != 0;','boolean log = (mask & 4) != 0;'),
    'HttpByteRangeParserTest':('for (int index = 0; index < 100; index++)','int value = index;',
        'Optional.of(value % 2 == 0 ? "bytes=" + value + "-" + value : "bytes=-0")'),
    'WebNativeRuntimeOwnedComponentTest':('final AtomicInteger verified = new AtomicInteger();','int index = verified.getAndIncrement();',
        'index == 0','? new StorageIdentity("schubert-api", "schubert-web")',': new StorageIdentity("schubert-data", "schubert-read")'),
}
BACKUP = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactFixture.java'
REPOSITORY = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/'
SUPPLEMENTAL = {
    REPOSITORY+'BatchRun.java':('RECORD','BatchRun'),REPOSITORY+'CleanupCounts.java':('RECORD','CleanupCounts'),
    REPOSITORY+'CleanupReason.java':('ENUM','CleanupReason'),REPOSITORY+'BatchStep.java':('ENUM','BatchStep'),
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/media/HttpByteRangeParser.java':('ENUM','Unsatisfiable'),
}


def declaration(text,name):
    pattern = r'\b(?:UUID|Instant|String|long|BatchRun|CleanupCounts)\s+'+name+r'\s*=\s*(.*?);'
    matches = list(re.finditer(pattern,text,re.S))
    if len(matches) != 1:
        raise ValueError('one exact fixture input declaration required')
    match, = matches
    initializer = match.group(1)
    stripped = re.sub(r'"(?:\\.|[^"\\])*"','0',initializer)
    calls = re.findall(r'\b([A-Za-z_$][A-Za-z0-9_$]*)\s*\(',stripped)
    if set(calls)-{'UUID','fromString','parse','repeat','BatchRun','CleanupCounts'}:
        raise ValueError('no Production factory/getter or unknown initializer')
    return dict(name=name,startLine=text.count('\n',0,match.start())+1,endLine=text.count('\n',0,match.end())+1,
        declarationSha256=data.sha(match.group().encode()),initializerSha256=data.sha(initializer.encode()),
        initializationKind='EXPLICIT_TEST_LITERAL_JDK_VALUE_OR_VALUE_PRESERVING_RECORD')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_path = data.BASE/'PG10658-direct-enum-constructor-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'0405725d0079434a86a86976aee0b204fd429d52af72ec6ac5f472387997d1e6')
    candidates = data.read_checked(prior_path.parent/'enum-input-reviews.json',prior['rowsSha256'])
    qmeta = data.read_checked(data.BASE/'PG10652-qualified-constructor-inputs-v1/manifest.json',
        'fbbf406acd3b6361fe5f27fb1636da77b16a817015e27cd9b43c807171ea9983')
    qualified = data.read_checked(data.BASE/'PG10652-qualified-constructor-inputs-v1/qualified-input-reviews.json',qmeta['qualifiedInputReviewsSha256'])
    original = data.read_checked(data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json',
        'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    originals = data.read_checked(data.BASE/'PG10646-constructor-literal-inputs-v1/input-reviews.json',original['inputReviewsSha256'])
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    sources = {}
    def source(path):
        assert path.startswith('src/') and path.endswith('.java')
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        sources[path] = data.sha(text.encode())
        return text
    backup = source(BACKUP)
    assert 'Public synthetic content' in backup
    hash_vectors = []
    for field,file,content in [('DUMP_HASH','schubert_nk.dump','PG166 public dump fixture\n'),
        ('CONFIG_HASH','config.tar','PG166 public configuration fixture\n'),
        ('CREDS_HASH','credentials.tar.age','PG166 public ciphertext fixture\n')]:
        declared = declaration(backup,field)
        match = re.search(r'\bString\s+'+field+r'\s*=\s*("[0-9a-f]{64}")\s*;',backup)
        assert match
        literal = json.dumps(content)
        assert 'child.resolve("'+file+'"),' in backup and literal in backup
        digest = hashlib.sha256(content.encode('ascii')).hexdigest()
        assert digest == json.loads(match.group(1))
        hash_vectors.append(dict(name=field,publicSynthetic=True,bytes=len(content.encode('ascii')),sha256=digest,definition=declared))
    supplemental = {}
    for path,(kind,name) in SUPPLEMENTAL.items():
        text = source(path)
        if kind == 'RECORD':
            review = record_review(text,name)
            assert review['kind'] == 'VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT'
        else:
            assert re.search(r'\benum\s+'+name+r'\b',text)
            review = dict(kind='EXPLICIT_ENUM_MEMBER_INPUT_ONLY_NOT_MAPPING_QUALIFICATION')
        supplemental[path] = review
    rows,counts,evidence = [],Counter(),{}
    for index,candidate in enumerate(candidates):
        if candidate['status'] != 'NAMED_INPUT_ORIGIN_PENDING':
            continue
        row = originals[qualified[candidate['priorQualifiedIndex']]['priorEntryIndex']]['original']
        path = row['path']
        text = source(path)
        assert sources[path] == row['sourceSha256']
        stem = Path(path).stem
        assert stem in DEFINITIONS
        if path not in evidence:
            declared = [declaration(text,n) for n in DEFINITIONS[stem]]
            controls = []
            for control in CONTROLS.get(stem,()):
                assert control in text
                controls.append(dict(text=control,sha256=data.sha(control.encode())))
            if stem in ('BackupArtifactVerifierTest','MorningBackupRetentionTest'):
                assert all('import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.'+v['name']+';' in text for v in hash_vectors)
            evidence[path] = dict(sourceSha256=sources[path],definitions=declared,controls=controls)
        expression = first_argument(text,row)
        assert data.sha(text[expression[0][1]:expression[-1][2]].encode()) == row['expectedExpressionSha256']
        if stem == 'WebNativeRuntimeOwnedComponentTest':
            status = 'CALLBACK_ORDINAL_PROPERTY_ONLY_PENDING_FULL_ORACLE'
            reason = 'Test-owned callback counter selects expected role by call order; this assertion alone does not bind each expected identity to an independently named path. No whole ownership/path acceptance.'
        elif stem in ('AuthenticationContextVerifierTest','RunReferenceRepositoryTest') or row['method'] == 'oneHundredConcurrentParsesHaveNoSharedState':
            status = 'FIXTURE_FINITE_LOOP_INPUT_STATIC_REVIEWED'
            reason = 'Explicit finite fixture inputs/control bits/index are used on expected side, not SUT result fields; whole fixture execution remains HOLD.'
        else:
            status = 'FIXTURE_DEFINED_INPUT_STATIC_REVIEWED'
            reason = 'Source-bound Test-local literals/JDK immutable values or validation-only record input; public Backup digest vectors independently checked; no Production algorithm output used.'
        counts[status] += 1
        rows.append(dict(priorEnumIndex=index,priorEnumSha256=data.sha(json.dumps(candidate,sort_keys=True,ensure_ascii=False).encode()),
            key=candidate['key'],sourceSha256=sources[path],status=status,reason=reason,
            fixtureEvidenceReference=path,wholeCaseFixtureQualified=False,productTestsExecuted=0))
    assert len(rows) == 38 and counts == {'FIXTURE_DEFINED_INPUT_STATIC_REVIEWED':34,
        'FIXTURE_FINITE_LOOP_INPUT_STATIC_REVIEWED':3,'CALLBACK_ORDINAL_PROPERTY_ONLY_PENDING_FULL_ORACLE':1}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'fixture-input-reviews.json',rows)
    data.write(OUT/'fixture-definitions.json',evidence)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        priorManifestSha256=data.sha(prior_path.read_bytes()),candidateRows=38,counts=dict(counts),
        rowsSha256=data.sha((OUT/'fixture-input-reviews.json').read_bytes()),definitionsSha256=data.sha((OUT/'fixture-definitions.json').read_bytes()),
        sourceHashes=sources,supplementalRecordAndEnumSourceReviews=supplemental,publicSyntheticHashVectors=hash_vectors,
        newFixtureInputSites=37,callbackPropertyStillUnqualified=1,remainingMethodInputs=66,
        previous62AndTwoCorrectedNotRecounted=True,productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,
        coverage=None,wholeOracleQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
