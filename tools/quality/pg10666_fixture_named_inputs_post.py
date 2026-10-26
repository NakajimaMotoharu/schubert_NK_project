"""Independent raw-span/fixture-definition check; no fixture, target or filesystem scenario execution."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10666-fixture-named-inputs-post-v1'
EXPECTED = {
    'InboxInspectionProgressBoundaryTest':{'ONE':'new UUID(0,1)','high':'UUID.fromString("80000000-0000-0000-0000-000000000000")'},
    'AuthSessionRevocationServiceTest':{'SESSION':'new UUID(0,1)'},
    'AuthSessionServiceTest':{'ID':'UUID.fromString("b2000000-0000-0000-0000-000000000001")'},
    'ArtemisExpiryPurgeClientTest':{'CUTOFF':'1_789_603_200_000L'},
    'BackupWorkerRequestTest':{'RUN':'UUID.fromString("11111111-2222-4333-8444-555555555555")',
        'START':'Instant.parse("2026-09-27T14:59:59.123456Z")'},
    'CleanupWorkerRequestTest':{'RUN':'UUID.fromString("31100027-2222-4333-8444-555555555555")',
        'ACTIVATION':'UUID.fromString("31100027-6666-4777-8888-999999999999")',
        'CUTOFF':'Instant.parse("2026-09-27T15:00:00Z")','DIGEST':'"0123456789abcdef".repeat(4)'},
    'CleanupRepositoryTest':{'RUN':'new BatchRun(new UUID(0,94),Instant.parse("2026-09-17T00:00:00Z"))','ZERO':'new CleanupCounts(0,0,0)'},
    'ExpiryAuditRepositoryTest':{'RUN':'new BatchRun(UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),Instant.parse("2026-09-12T15:00:00.000500Z"))',
        'START':'Instant.parse("2026-09-12T15:00:01Z")','END':'Instant.parse("2026-09-12T15:00:02Z")',
        'EXPIRY_CUTOFF':'Instant.parse("2026-09-05T15:00:00.000500Z")'},
    'HttpByteRangeParserTest':{'TOTAL':'2_097_155'},
}


def validate_initializer(actual,expected):
    if canonical(actual) != canonical(expected):
        raise ValueError('exact literal/JDK immutable fixture input required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10664-fixture-named-inputs-v1/manifest.json'
    primary = data.read_checked(primary_path,'26b1348c8742bff694d2366d32726545b77554344cefe6b0cb7da5d325f99ba2')
    rows = data.read_checked(primary_path.parent/'fixture-input-reviews.json',primary['rowsSha256'])
    evidence = data.read_checked(primary_path.parent/'fixture-definitions.json',primary['definitionsSha256'])
    prior_path = data.BASE/'PG10658-direct-enum-constructor-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'0405725d0079434a86a86976aee0b204fd429d52af72ec6ac5f472387997d1e6')
    candidates = data.read_checked(prior_path.parent/'enum-input-reviews.json',prior['rowsSha256'])
    qmeta = data.read_checked(data.BASE/'PG10652-qualified-constructor-inputs-v1/manifest.json',
        'fbbf406acd3b6361fe5f27fb1636da77b16a817015e27cd9b43c807171ea9983')
    qualified = data.read_checked(data.BASE/'PG10652-qualified-constructor-inputs-v1/qualified-input-reviews.json',qmeta['qualifiedInputReviewsSha256'])
    first = data.read_checked(data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json',
        'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    originals = data.read_checked(data.BASE/'PG10646-constructor-literal-inputs-v1/input-reviews.json',first['inputReviewsSha256'])
    wanted = {i for i,r in enumerate(candidates) if r['status'] == 'NAMED_INPUT_ORIGIN_PENDING'}
    assert len(rows) == len(wanted) == 38 and {r['priorEnumIndex'] for r in rows} == wanted
    for path,digest in primary['sourceHashes'].items():
        assert path.startswith('src/') and data.sha((data.ROOT/path).read_bytes()) == digest
    definitions = 0
    for path,proof in evidence.items():
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == proof['sourceSha256']
        expected = EXPECTED.get(Path(path).stem,{})
        assert {d['name'] for d in proof['definitions']} == set(expected)
        for d in proof['definitions']:
            match = re.search(r'\b(?:UUID|Instant|String|long|BatchRun|CleanupCounts)\s+'+d['name']+r'\s*=\s*(.*?);',text,re.S)
            assert match and data.sha(match.group().encode()) == d['declarationSha256']
            assert data.sha(match.group(1).encode()) == d['initializerSha256']
            validate_initializer(match.group(1),expected[d['name']])
            assert len(re.findall(r'\b'+d['name']+r'\s*=(?!=)',text)) == 1
            definitions += 1
        for control in proof['controls']:
            assert control['text'] in text and data.sha(control['text'].encode()) == control['sha256']
    assert definitions == 18
    counts = Counter()
    for result in rows:
        candidate = candidates[result['priorEnumIndex']]
        assert data.sha(json.dumps(candidate,sort_keys=True,ensure_ascii=False).encode()) == result['priorEnumSha256']
        row = originals[qualified[candidate['priorQualifiedIndex']]['priorEntryIndex']]['original']
        assert result['key'] == candidate['key'] and result['fixtureEvidenceReference'] == row['path']
        text = (data.ROOT/row['path']).read_text()
        begin,end = matching_span(text,row)
        assert data.sha(text[begin:end].encode()) == row['expectedExpressionSha256']
        if row['method'] == 'verifyOwn':
            assert result['status'] == 'CALLBACK_ORDINAL_PROPERTY_ONLY_PENDING_FULL_ORACLE'
            assert 'int index = verified.getAndIncrement();' in text and 'No whole ownership/path acceptance' in result['reason']
        assert not result['wholeCaseFixtureQualified'] and result['productTestsExecuted'] == 0
        counts[result['status']] += 1
    assert counts == primary['counts'] == {'FIXTURE_DEFINED_INPUT_STATIC_REVIEWED':34,
        'FIXTURE_FINITE_LOOP_INPUT_STATIC_REVIEWED':3,'CALLBACK_ORDINAL_PROPERTY_ONLY_PENDING_FULL_ORACLE':1}
    backup_path = next(p for p in primary['sourceHashes'] if p.endswith('/BackupArtifactFixture.java'))
    backup = (data.ROOT/backup_path).read_text()
    vectors = [('DUMP_HASH','PG166 public dump fixture\n',26),('CONFIG_HASH','PG166 public configuration fixture\n',35),
        ('CREDS_HASH','PG166 public ciphertext fixture\n',32)]
    for name,value,length in vectors:
        match = re.search(r'\bString\s+'+name+r'\s*=\s*("[0-9a-f]{64}")\s*;',backup)
        assert match and json.dumps(value) in backup and len(value.encode('ascii')) == length
        digest = hashlib.sha256(value.encode('ascii')).hexdigest()
        assert digest == json.loads(match.group(1))
        assert next(v for v in primary['publicSyntheticHashVectors'] if v['name'] == name)['sha256'] == digest
    rejected = 0
    for wrong in ('ProductionFactory.currentId()','actual','new UUID(1,0)'):
        try:
            validate_initializer(wrong,'new UUID(0,1)')
        except ValueError:
            rejected += 1
        else:
            raise AssertionError('unknown or SUT-generated initializer accepted')
    assert rejected == 3
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),priorCandidateRows=38,independentRawSpans=38,
        independentlyVerifiedFixtureDeclarations=18,publicSyntheticHashVectors=3,metadataNegativeVectors=3,
        fixtureInputSitesReviewed=37,callbackPropertyStillUnqualified=1,remainingMethodInputs=66,
        previous62AndTwoCorrectedNotRecounted=True,productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,
        coverage=None,wholeOracleQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
