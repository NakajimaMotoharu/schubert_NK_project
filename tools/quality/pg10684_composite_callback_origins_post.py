"""Independent raw-source/finite-fixture audit; no DB, descriptor, broker or Product execution."""
import datetime
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10684-composite-callback-origins-post-v1'
BATCH = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java'
WEB = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntimeOwnedComponentTest.java'
ANCHORS = {
    BATCH:('for (int mode = 0; mode < 5; mode++) mdb590Scenarios(37 + mode, "", "", false, mode);',
        'int scenario = seed * 6 + index;', 'priorMode >= 0 ? 1 : seed == 0 ? 6 : 3',
        'java.time.LocalDate.of(2010, 1, 1).plusDays(scenario)',
        'Instant began = fixtureDate.atStartOfDay(java.time.ZoneOffset.UTC).toInstant();',
        'var run = new BatchRun(new UUID(590001, scenario + 1), began.minusSeconds(32400));',
        'var priorRun = new BatchRun(new UUID(595001, scenario + 1), run.cutoff().plusSeconds(1));',
        'long priorId = 595000000L + scenario;',
        'var literalHandle = new BatchStepAttempt(priorId,priorRun,BatchStep.CLEAN_EXPIRY,1,began.minusSeconds(10),false);',
        'var literalAudit = new ExpiryAuditRepository.Snapshot("SUCCESS",priorRun.cutoff().minusSeconds(604800),2L,1L,1,1,0,17,began.minusSeconds(9),null,null);',
        'sql.setLong(1, priorId);', 'sql.setObject(2, priorRun.id());',
        'sql.setObject(4, began.minusSeconds(10).atOffset(java.time.ZoneOffset.UTC));',
        'sql.setObject(5, began.minusSeconds(9).atOffset(java.time.ZoneOffset.UTC));'),
    WEB:('final AtomicInteger verified = new AtomicInteger();','int index = verified.getAndIncrement();',
        'index == 0 ? new StorageIdentity("schubert-api", "schubert-web") : new StorageIdentity("schubert-data", "schubert-read")',
        'entry.getValue()', 'entry.getKey().atDirectory(Files::isDirectory)',
        'entry -> verification.run(entry)',
        'case "nk.web.storage.transfer-root" -> "transfer";', 'case "nk.web.storage.asset-root" -> "assets";'),
}


def contains(text,fragment):
    whole,part = canonical(text),canonical(fragment)
    return bool(part) and any(whole[i:i+len(part)] == part for i in range(len(whole)-len(part)+1))


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10682-composite-callback-origins-v1/manifest.json'
    primary = data.read_checked(primary_path,'25cdcfc878ee4ecd5ef06193f77c65411e52a9cc7dd7c55bd3e075552bff9e61')
    rows = data.read_checked(primary_path.parent/'origin-reviews.json',primary['rowsSha256'])
    evidence = data.read_checked(primary_path.parent/'source-evidence.json',primary['evidenceSha256'])
    contracts = data.read_checked(primary_path.parent/'supplemental-contracts.json',primary['supplementalSha256'])
    original_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    original = data.read_checked(original_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    entries = data.read_checked(original_path.parent/'input-reviews.json',original['inputReviewsSha256'])
    assert len(rows) == 2 and {r['key']['path'] for r in rows} == {BATCH,WEB}
    for result in rows:
        entry = entries[result['priorEntryIndex']]
        assert data.sha(json.dumps(entry,sort_keys=True,ensure_ascii=False).encode()) == result['priorEntrySha256']
        row = entry['original']
        assert result['key'] == {k:row[k] for k in ('path','method','line','expectedExpressionSha256')}
        path = row['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == result['sourceSha256'] == evidence[path]['sha256']
        start,end = matching_span(text,row)
        assert text[start:end] == result['expression'] and data.sha(text[start:end].encode()) == row['expectedExpressionSha256']
        for span in evidence[path]['ranges']:
            assert ''.join(text.splitlines(keepends=True)[span['first']-1:span['last']]) == span['text']
        for fragment in ANCHORS[path]:
            assert contains(text,fragment)
        expected_status = 'FINITE_COMPOSITE_TEST_INPUT_ORIGIN_STATIC_REVIEWED' if path == BATCH else 'CALLBACK_ORDINAL_SUPPLEMENTAL_PROPERTY_NOT_PATH_OWNER_ORACLE'
        assert result['status'] == expected_status and not result['wholeCaseFixtureQualified']
    for proof in contracts:
        text = (data.ROOT/proof['path']).read_text()
        assert data.sha(text.encode()) == proof['sha256']
        if proof['path'].endswith('/OwnedTransferDirectory.java'):
            assert 'Inspect this held directory, not its replaceable configured path' in text
            assert contains(text,'execute(Path.of("/proc/self/fd", Integer.toString(descriptor)), operation)')
        else:
            assert proof['path'].endswith('/BatchStepAttempt.java')
            assert proof['review']['kind'] == 'VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT'
            assert not contains(text,'this.id = id')
    assert contains('a(); b();','a();') and not contains('a(); b();','a b')
    assert not contains('var priorId = actual.id();','long priorId = 595000000L + scenario;')
    assert not contains('new BatchStepAttempt(actual.handle(),priorRun,step,1,time,false)',
        'new BatchStepAttempt(priorId,priorRun,BatchStep.CLEAN_EXPIRY,1,began.minusSeconds(10),false)')
    vectors = []
    for mode,date in enumerate(('2010-08-11','2010-08-17','2010-08-23','2010-08-29','2010-09-04')):
        seed = 37+mode
        scenario = seed*6
        day = datetime.date(2010,1,1)+datetime.timedelta(days=scenario)
        assert day.isoformat() == date
        began = datetime.datetime.combine(day,datetime.time(),datetime.timezone.utc)
        prior_cutoff = began-datetime.timedelta(seconds=32400-1)
        vectors.append(dict(mode=mode,seed=seed,index=0,scenario=scenario,priorId=595000000+scenario,
            began=began.isoformat(),priorCutoff=prior_cutoff.isoformat(),
            expiryCutoff=(prior_cutoff-datetime.timedelta(days=7)).isoformat(),
            handleStarted=(began-datetime.timedelta(seconds=10)).isoformat(),
            auditEnded=(began-datetime.timedelta(seconds=9)).isoformat(),inputVectorOnlyNotExecutedCase=True))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'finite-fixture-input-vectors.json',vectors)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),independentRawSpans=2,sourceAnchors=sum(map(len,ANCHORS.values())),
        finiteInputMetadataVectors=5,negativeSourceMetadataVectors=3,
        vectorsSha256=data.sha((OUT/'finite-fixture-input-vectors.json').read_bytes()),
        totalInputProvenanceReviewed=160,previousCorrections=2,supplementalProperties=6,unclassifiedInputOriginSites=0,
        wholePathOwnerOracleStillUnproven=True,wholeOracleQualified=False,productTestsExecuted=0,
        targetClassLoaded=False,targetCompilation=False,coverage=None,externalActions=0,newAccepted=0,
        formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
