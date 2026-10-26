"""Source-bound fixture inputs vs opaque identity/hash properties; no Product execution."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10676-remaining-constructor-origins-v1'
FIELDS = {
    'UserQuerySqlContractTest':('USERNAME','CREATED','UPDATED','LAST_LOGIN','LOCKED_UNTIL'),
    'QuestionSqlContractTest':('RECEIPT','USERNAME','ANSWER','SUMMARY','BODY','NOW','ANSWERED','USER','ADMIN'),
    'InspectorApplicationTest':('RUN',),'AuthenticationInboxCleanupTest':('MESSAGE',),
    'InboxCleanupNonAuthenticationTest':(),'InspectionRunExecutorTest':('RUN',),
    'QuestionQueryInboxCleanupTest':('MESSAGE','RUN'),
    'MaintenanceRunFilesTest':('RUN_ID','ACT_ID','RUN','ACTIVATION','done'),
    'MaintenanceRunRetirementTest':('OTHER',),
    'MorningCurrentInvalidationTest':('BOOT','EPOCH','RUN','ACTIVE','ACTIVATION'),
    'MorningNewRunAdmissionTest':('RUN','ACTIVATION'),
    'MorningOriginalCompletionTest':('id',),
    'MonitoringPolicyEngineTest':('TIME',),'RootStartupContextTest':('BOOT','INV'),
    'MorningExpirySessionTest':('NOW',),'TerminalNativeCoverageProfileTest':(),
    'LogSearchWireClientTest':(),'ReceiptReferenceRepositoryTest':('ID','TIME'),
}
FRAGMENTS = {
    'QuestionSqlContractTest':('for (var actor : List.of(USER, ADMIN))','for (boolean deleted : List.of(false, true))'),
    'InspectionRunExecutorTest':('private static InspectionProgress progress(long count, long held, boolean complete) { return new InspectionProgress(RUN,count == 0 ? Optional.empty() : Optional.of(new UUID(0, count)),count,count - held,held,complete); }',),
    'MaintenanceRunFilesTest':('assertEquals(done, s.complete(done));','assertEquals(DONE0, Files.readString(f.attempts.resolve(ACT_ID + ".done")));'),
    'RootStartupContextTest':('BOOT.trim()',),
    'MorningExpirySessionTest':('NOW.plusSeconds(15)',),
    'TerminalNativeCoverageProfileTest':('for (var service : ServiceConfigFiles.Service.values())',),
    'LogSearchWireClientTest':('for (boolean optional : List.of(false, true))',),
    'RunReferenceRepositoryTest':('for (int mask = 0; mask < 8; mask++)','for (boolean consistent : List.of(false, true))',
        'boolean history = (mask & 1) != 0;','boolean inbox = (mask & 2) != 0;','boolean log = (mask & 4) != 0;',
        'assertEquals(history, value.hasBatchHistory());','assertEquals(inbox, value.hasInboxProgress());',
        'assertEquals(log, value.hasLogProgress());','assertEquals(consistent, value.identityConsistent());',
        'assertEquals(mask != 0, value.anyReference());'),
}
OPAQUE = {'BackupHealthMonitorTest','DlqHealthMonitorTest','IntegrityHealthMonitorTest','RestartHealthMonitorTest'}


def contains_tokens(text,fragment):
    haystack,needle = canonical(text),canonical(fragment)
    return bool(needle) and any(haystack[i:i+len(needle)] == needle for i in range(len(haystack)-len(needle)+1))


def declarations(text,name):
    pattern = r'\b(?:UUID|Instant|String|AuthenticatedActor|InspectionRun|BatchRun|MaintenanceActivation|var)\s+'+name+r'\s*=\s*(.*?);'
    found = list(re.finditer(pattern,text,re.S))
    assert found
    return [dict(name=name,line=text.count('\n',0,m.start())+1,text=m.group(),
        initializer=m.group(1),sha256=data.sha(m.group().encode())) for m in found]


def classification(stem):
    if stem in OPAQUE:
        return 'OPAQUE_EVENT_IDENTITY_ONLY_NOT_CONTENT_ORACLE'
    if stem == 'RunReferenceRepositoryTest':
        return 'EQUAL_VALUE_HASH_SUPPLEMENTAL_PROPERTY_NOT_NUMERIC_ORACLE'
    if stem == 'MorningDatabaseSessionTest':
        return 'COMPOSITE_DB_FIXTURE_INPUT_ORIGIN_PENDING'
    assert stem in FIELDS
    return 'FIXTURE_HELPER_JDK_INPUTS_STATIC_REVIEWED'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_path = data.BASE/'PG10670-jdk-factory-constructor-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'8ff711165cb406394f9159d528b9764bac5b349566b756de38431c5b206ce247')
    candidates = data.read_checked(prior_path.parent/'jdk-input-reviews.json',prior['rowsSha256'])
    first_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    first = data.read_checked(first_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    originals = data.read_checked(first_path.parent/'input-reviews.json',first['inputReviewsSha256'])
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    assert contains_tokens('x = 1; y = 2;', 'x=1;')
    assert not contains_tokens('x = 1; y = 2;', 'x = 2;')
    assert not contains_tokens('x = 1; y = 2;', 'x y')
    assert not contains_tokens('x = 1; y = 2;', '')
    rows,evidence,counts = [],{},Counter()
    for index,candidate in enumerate(candidates):
        if candidate['status'] != 'METHOD_OR_NAMED_INPUT_ORIGIN_PENDING':
            continue
        row = originals[candidate['priorEntryIndex']]['original']
        path = row['path']
        assert path.startswith('src/') and '/src/test/java/' in path
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == normal['begin']['inputHashes'][path]
        tokens = first_argument(text,row)
        expression = text[tokens[0][1]:tokens[-1][2]]
        assert data.sha(expression.encode()) == row['expectedExpressionSha256']
        stem = Path(path).stem
        status = classification(stem)
        if path not in evidence:
            fields = [d for name in FIELDS.get(stem,()) for d in declarations(text,name)]
            fragments = list(FRAGMENTS.get(stem,()))
            if stem in OPAQUE:
                fragments += ['var event = sample(', 'assertSame(event, populated.event().orElseThrow());']
            for fragment in fragments:
                assert contains_tokens(text,fragment)
            evidence[path] = dict(sourceSha256=row['sourceSha256'],definitions=fields,fragments=fragments)
        counts[status] += 1
        rows.append(dict(priorJdkIndex=index,priorJdkEntrySha256=data.sha(json.dumps(candidate,sort_keys=True,ensure_ascii=False).encode()),
            key=candidate['key'],sourceSha256=row['sourceSha256'],status=status,expression=expression,
            wholeCaseFixtureQualified=False,productTestsExecuted=0))
    expected = {'FIXTURE_HELPER_JDK_INPUTS_STATIC_REVIEWED':40,'OPAQUE_EVENT_IDENTITY_ONLY_NOT_CONTENT_ORACLE':4,
        'EQUAL_VALUE_HASH_SUPPLEMENTAL_PROPERTY_NOT_NUMERIC_ORACLE':1,'COMPOSITE_DB_FIXTURE_INPUT_ORIGIN_PENDING':1}
    assert len(rows) == 46 and counts == expected
    imported = next(p for p in normal['begin']['inputHashes'] if p.endswith('/MaintenanceRetirementRecordsTest.java'))
    source = (data.ROOT/imported).read_text()
    assert data.sha(source.encode()) == normal['begin']['inputHashes'][imported]
    imported_fields = declarations(source,'CUTOFF')
    evidence[imported] = dict(sourceSha256=data.sha(source.encode()),definitions=imported_fields,fragments=[])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'origin-reviews.json',rows)
    data.write(OUT/'source-evidence.json',evidence)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        priorManifestSha256=data.sha(prior_path.read_bytes()),candidateRows=46,counts=dict(counts),newInputProvenanceReviewed=40,
        prior119NotRecounted=True,previousCorrections=2,newCorrections=0,totalInputProvenanceReviewed=159,
        opaqueOrSupplementalProperties=5,remainingCompositeInputOrigins=1,callbackStillUnqualified=1,
        rowsSha256=data.sha((OUT/'origin-reviews.json').read_bytes()),evidenceSha256=data.sha((OUT/'source-evidence.json').read_bytes()),
        productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,coverage=None,wholeOracleQualified=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
