"""Independent raw-span, literal declaration and property-limit audit; no Product execution."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span
from pg10398_role_view_preflight import canonical
from pg10588_record_constructor_review import record_review

OUT = data.BASE/'PG10678-remaining-constructor-origins-post-v1'
EXPECTED = {
    'UserQuerySqlContractTest':{'USERNAME':'"u3"','CREATED':'Instant.parse("2026-01-01T00:00:00Z")',
        'UPDATED':'Instant.parse("2026-09-01T00:00:00Z")','LAST_LOGIN':'Instant.parse("2026-09-07T00:00:00.123Z")',
        'LOCKED_UNTIL':'Instant.parse("2026-09-09T00:00:00.456Z")'},
    'QuestionSqlContractTest':{'RECEIPT':'"00000000000000000000000001"','USERNAME':'"unit7"','ANSWER':'"answer"',
        'SUMMARY':'"😀".repeat(100)','BODY':'SUMMARY+"tail"','NOW':'Instant.parse("2026-10-01T00:00:00.123Z")',
        'ANSWERED':'Instant.parse("2026-10-01T00:00:01.123Z")','USER':'new AuthenticatedActor(7,USERNAME,Role.USER)',
        'ADMIN':'new AuthenticatedActor(8,"admin8",Role.ADMIN)'},
    'InspectorApplicationTest':{'RUN':'new InspectionRun(new UUID(0,42),Instant.parse("2026-09-17T00:00:00.123Z"))'},
    'AuthenticationInboxCleanupTest':{'MESSAGE':'new UUID(0,101)'},
    'InspectionRunExecutorTest':{'RUN':'new InspectionRun(new UUID(0,91),Instant.parse("2026-09-17T00:00:00Z"))'},
    'QuestionQueryInboxCleanupTest':{'MESSAGE':'new UUID(0,101)',
        'RUN':'new InspectionRun(new UUID(0,42),Instant.parse("2026-09-17T00:00:00.123Z"))'},
    'MaintenanceRunFilesTest':{'RUN_ID':'"12345678-9abc-def0-8123-456789abcdef"',
        'ACT_ID':'"fedcba98-7654-3210-8fed-cba987654321"',
        'RUN':'new BatchRun(UUID.fromString(RUN_ID),Instant.parse("2026-09-12T04:05:06.123456Z"))',
        'ACTIVATION':'new MaintenanceActivation(RUN,UUID.fromString(ACT_ID))'},
    'MaintenanceRetirementRecordsTest':{'CUTOFF':'"2025-01-01T00:00:00.000000Z"'},
    'MaintenanceRunRetirementTest':{'OTHER':'"00000000-0000-0000-0000-000000000001"'},
    'MorningCurrentInvalidationTest':{'BOOT':'UUID.fromString("00000000-0000-0000-0000-000000000344")',
        'EPOCH':'UUID.fromString("00000000-0000-0000-0000-000000000345")',
        'RUN':'UUID.fromString("00000000-0000-0000-0000-000000000346")',
        'ACTIVE':'UUID.fromString("00000000-0000-0000-0000-000000000347")',
        'ACTIVATION':'new MaintenanceActivation(new BatchRun(RUN,Instant.parse("2026-09-28T05:00:00Z")),ACTIVE)'},
    'MorningNewRunAdmissionTest':{'RUN':'UUID.fromString("00000000-0000-0000-0000-000000000341")',
        'ACTIVATION':'UUID.fromString("00000000-0000-0000-0000-000000000342")'},
    'MorningOriginalCompletionTest':{'id':'UUID.fromString("00000000-0000-0000-0000-000000000454")'},
    'MonitoringPolicyEngineTest':{'TIME':'Instant.parse("2026-10-23T00:00:00Z")'},
    'RootStartupContextTest':{'BOOT':'"11111111-1111-1111-1111-111111111111\\n"','INV':'"1".repeat(32)'},
    'MorningExpirySessionTest':{'NOW':'Instant.parse("2026-09-13T02:00:00Z")'},
    'ReceiptReferenceRepositoryTest':{'ID':'"00000000000000000000000001"','TIME':'Instant.parse("2026-10-04T00:00:00.123Z")'},
}


def exact_initializer(actual,expected):
    if canonical(actual) != canonical(expected):
        raise ValueError('fixed reviewed fixture input required; names alone are not evidence')


def at_line(text,raw,line):
    suffix = ''.join(text.splitlines(keepends=True)[line-1:]) if line > 0 else ''
    offset = suffix.find(raw)
    return offset >= 0 and '\n' not in suffix[:offset]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    assert at_line('var id=1;\nother();\nvar id=1;\n','var id=1;',1)
    assert at_line('var id=1;\nother();\nvar id=1;\n','var id=1;',3)
    assert not at_line('var id=1;\nother();\nvar id=1;\n','var id=1;',2)
    primary_path = data.BASE/'PG10676-remaining-constructor-origins-v1/manifest.json'
    primary = data.read_checked(primary_path,'5ab5c84a06f3100035ccce7ce0055414a20bcda47eb3f6374068150280451b1e')
    rows = data.read_checked(primary_path.parent/'origin-reviews.json',primary['rowsSha256'])
    evidence = data.read_checked(primary_path.parent/'source-evidence.json',primary['evidenceSha256'])
    prior_path = data.BASE/'PG10670-jdk-factory-constructor-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'8ff711165cb406394f9159d528b9764bac5b349566b756de38431c5b206ce247')
    candidates = data.read_checked(prior_path.parent/'jdk-input-reviews.json',prior['rowsSha256'])
    original_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    original = data.read_checked(original_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    originals = data.read_checked(original_path.parent/'input-reviews.json',original['inputReviewsSha256'])
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    wanted = {i for i,r in enumerate(candidates) if r['status'] == 'METHOD_OR_NAMED_INPUT_ORIGIN_PENDING'}
    assert len(rows) == len(wanted) == 46 and {r['priorJdkIndex'] for r in rows} == wanted
    declarations_checked = 0
    for path,proof in evidence.items():
        assert path.startswith('src/') and '/src/test/java/' in path
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == proof['sourceSha256'] == normal['begin']['inputHashes'][path]
        stem = Path(path).stem
        expected = EXPECTED.get(stem,{})
        assert {d['name'] for d in proof['definitions']} == set(expected)|({'done'} if stem == 'MaintenanceRunFilesTest' else set())
        for definition in proof['definitions']:
            raw = definition['text']
            assert raw in text and data.sha(raw.encode()) == definition['sha256']
            assert at_line(text,raw,definition['line'])
            if definition['name'] == 'done':
                continue  # Different local scopes are not treated as one declaration.
            exact_initializer(definition['initializer'],expected[definition['name']])
            declarations_checked += 1
        for fragment in proof['fragments']:
            # Token subsequence, not list-as-single-element membership (BUG1858).
            whole,part = canonical(text),canonical(fragment)
            assert part and any(whole[i:i+len(part)] == part for i in range(len(whole)-len(part)+1))
    counts = Counter()
    for result in rows:
        candidate = candidates[result['priorJdkIndex']]
        assert data.sha(json.dumps(candidate,sort_keys=True,ensure_ascii=False).encode()) == result['priorJdkEntrySha256']
        row = originals[candidate['priorEntryIndex']]['original']
        assert result['key'] == candidate['key'] == {k:row[k] for k in ('path','method','line','expectedExpressionSha256')}
        path = row['path']
        text = (data.ROOT/path).read_text()
        start,end = matching_span(text,row)
        assert text[start:end] == result['expression'] and data.sha(text[start:end].encode()) == row['expectedExpressionSha256']
        stem = Path(path).stem
        if stem.endswith('HealthMonitorTest'):
            expected_status = 'OPAQUE_EVENT_IDENTITY_ONLY_NOT_CONTENT_ORACLE'
            assert re.search(r'var event\s*=\s*sample\(',text)
            assert 'assertSame(event, populated.event().orElseThrow());' in text
        elif stem == 'RunReferenceRepositoryTest':
            expected_status = 'EQUAL_VALUE_HASH_SUPPLEMENTAL_PROPERTY_NOT_NUMERIC_ORACLE'
            assert text[start:end].rstrip().endswith('.hashCode()')
            assert 'assertEquals(mask != 0, value.anyReference());' in text
        elif stem == 'MorningDatabaseSessionTest':
            expected_status = 'COMPOSITE_DB_FIXTURE_INPUT_ORIGIN_PENDING'
            assert 'literalHandle' in result['expression'] and 'literalAudit' in result['expression']
        else:
            expected_status = 'FIXTURE_HELPER_JDK_INPUTS_STATIC_REVIEWED'
        assert result['status'] == expected_status
        if stem == 'MaintenanceRunFilesTest':
            local = max((d for d in evidence[path]['definitions'] if d['name'] == 'done' and d['line'] < row['line']),key=lambda d:d['line'])
            exact_initializer(local['initializer'],'new MaintenanceCompletion(ACTIVATION,Instant.parse("2026-09-12T05:06:07.234567Z"),MaintenanceCompletion.Outcome.SUCCESS)')
            assert row['method'] == 'doneAfterRealSessionRetainsTypedDataReferenceButRejectsPendingCapability'
        assert not result['wholeCaseFixtureQualified'] and result['productTestsExecuted'] == 0
        counts[expected_status] += 1
    assert counts == primary['counts'] == {'FIXTURE_HELPER_JDK_INPUTS_STATIC_REVIEWED':40,
        'OPAQUE_EVENT_IDENTITY_ONLY_NOT_CONTENT_ORACLE':4,'EQUAL_VALUE_HASH_SUPPLEMENTAL_PROPERTY_NOT_NUMERIC_ORACLE':1,
        'COMPOSITE_DB_FIXTURE_INPUT_ORIGIN_PENDING':1}
    contracts = []
    for name in ('AuthenticatedActor','InspectionRun','BatchRun','MaintenanceActivation','MaintenanceCompletion'):
        path, = [p for p in normal['begin']['inputHashes'] if '/src/main/java/' in p and p.endswith('/'+name+'.java')]
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        review = record_review(text,name)
        assert review['kind'] == 'VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT'
        contracts.append(dict(path=path,sha256=data.sha(text.encode()),review=review))
    for actual in ('MainFactory.actual()','UUID.fromString("00000000-0000-0000-0000-000000000999")'):
        try:
            exact_initializer(actual,'UUID.fromString("00000000-0000-0000-0000-000000000341")')
        except ValueError:
            pass
        else:
            raise AssertionError('nonindependent/changed fixture must be rejected')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'constructor-input-contracts.json',contracts)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),independentRawSpans=46,counts=dict(counts),
        fixedDeclarationsChecked=declarations_checked,localDoneScopeSelected=True,extraValuePreservingConstructorContracts=5,
        contractsSha256=data.sha((OUT/'constructor-input-contracts.json').read_bytes()),initializerNegativeVectors=2,
        duplicateDeclarationPositionVectors=3,
        identityContentNotQualified=True,hashNumericOracleNotQualified=True,compositeAndCallbackStillPending=2,
        productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,coverage=None,wholeOracleQualified=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
