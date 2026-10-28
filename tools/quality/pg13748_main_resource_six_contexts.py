"""Six exact resource ownership contexts; no target execution or diagnostic suppression."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13748-main-resource-six-contexts-v1'
NORMAL = ('PG13596-lgs-remaining-two-branches-v1','1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
TARGETS = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/OperationFingerprint.java':('25f0c77746cdb01ce938f83fe0b019929f0aeb2e073db4f043abb3a41ba0995b','WBS-P006-01',{'field':'PMD-00127'}),
 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission.java':('4c0d9cd86b28b98d08d223dbb6f87c80f40d1b5226a9361add1ba28ea327fd2c','WBS-P019-01',{'query':'PMD-06101','values':'PMD-06102'}),
 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseAdmission.java':('667d73ca5509235a18c393910d9cbea603bf4acc615a4536b66b6993b822aa7e','WBS-P019-01',{'values':'PMD-06114'}),
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebOutboxObservationRepository.java':('8eead2d8cdf54cec5ce702117a34074c7d55b5ea454cfc8f001f770eae09d5c5','WBS-P018-09',{'statement':'PMD-07385','rows':'PMD-07386'})}
DEPENDENCIES = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/CanonicalField.java':'427b37bf360f201bd1509e336aa435f2a1db77c9f782b842aa2bf16fdcc28e3a',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/CanonicalRequest.java':'ae5d61f51e59329ffcccf18c702a430fc15d4e3731b2ffb5544ec9788a4ba2eb',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/WipingByteArrayOutputStream.java':'1f751a0267c7d9f894806d67e5b9b3c05955038353d6f6bd6a44cfe3bd1217de',
 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures.java':'bf179887c2496723d5ddb4ee0be02c5e599ecba781f5b8338367bb21648627a5'}
REASONS = {
 'PMD-00127':'field is borrowed from caller-owned CanonicalRequest.fields, not acquired by the loop. Closing it here mutates later fingerprint lookups. value() clones and writeValue finally wipes that temporary clone; request.close is the terminal caller-scope field owner. Local wiping output is independently TWR-owned.',
 'PMD-06101':'query aliases the identical acquired statement through required(statement), never an independently acquired resource. The enclosing statement finally closes once after rows; closing query too would duplicate ownership. Explicit primary/secondary precedence is maintained by JdbcAdmissionFailures.',
 'PMD-06102':'values aliases the identical acquired rows through required(rows), not a new ResultSet. The inner finally closes rows once on all success/failure exits, then statement closes. Neither helper nor this alias owns or closes the borrowed Connection.',
 'PMD-06114':'values aliases required(rows) unchanged. The rows finally closes the acquired object once before statement; manual close preserves unknown-vs-SQL exception precedence and redacted secondary. No Connection ownership is acquired.',
 'PMD-07385':'statement acquisition is immediately null-checked and entered into Java9 try(statement), before setQueryTimeout/executeQuery. Nested result scope closes first, statement closes even on acquisition/read/close failure. Borrowed connection remains unchanged.',
 'PMD-07386':'rows acquisition is immediately null-checked then entered into nested try(rows). Result close precedes statement close and return publication. Java TWR preserves primary/suppressed order; no successful partial observation escapes.'}
IDS = set(REASONS)

def source_guards(path,text):
    if path.endswith('/OperationFingerprint.java'):
        assert 'for (CanonicalField field : request.fields()) {' in text and 'writeValue(output, field.value());' in text
        assert 'field.close(' not in text and 'try (var output = new WipingByteArrayOutputStream()) {' in text
        assert 'Arrays.fill(value, (byte) 0);' in text
    elif path.endswith('/WebOutboxObservationRepository.java'):
        assert text.count('try (statement) {') == text.count('try (rows) {') == 1
        assert 'if (statement == null) throw new SQLException(INVALID);\n    try (statement) {' in text
        assert 'if (rows == null) throw new SQLException(INVALID);\n      try (rows) {' in text
        assert all(x not in text for x in ['connection.close(','connection.commit(','connection.rollback(','connection.setReadOnly('])
    else:
        assert 'var values = required(rows);' in text and text.count('rows.close();') == text.count('statement.close();') == 1
        assert 'if (JdbcAdmissionFailures.replace(rowFailure, secondary)) throw secondary;' in text
        assert 'if (JdbcAdmissionFailures.replace(primary, secondary)) throw secondary;' in text
        assert 'values.close(' not in text and 'query.close(' not in text and 'connection.close(' not in text
        if path.endswith('/SchemaHistoryAdmission.java'):assert 'var query = required(statement);' in text

def rows():
    normal = data.read_checked(data.BASE/NORMAL[0]/'manifest.json',NORMAL[1]);assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    for path,pin in DEPENDENCIES.items():assert data.sha((data.ROOT/path).read_bytes()) == hashes[path] == pin
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result = []
    for path,(pin,owner,fields) in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == pin;source_guards(path,text)
        ownership = canonical(path,logical);assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        selected = [r for r in facts if r['path'] == path and r['rule'] == 'CloseResource'];assert len(selected) == len(fields)
        for r in selected:
            a = r['attributes'];variable = a['variable'];identity = fields[variable];old, = [v for v in original if v['id'] == identity]
            assert old['path'] == path and old['rule'] == r['rule'] and old['attributes'] == a and old['inputSha256'] == r['sourceSha256'] == pin
            start,end,value = span(text,a);assert value == variable
            result.append(dict(id=identity,path=path,source=SOURCE,sourceSha256=pin,rule=r['rule'],variable=variable,attributes=a,originalRowSha256=old['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),reason=REASONS[identity],disposition='OWNERSHIP_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership))
    assert len(result) == 6 and {r['id'] for r in result} == IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();result = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,dependencySourceHashes=DEPENDENCIES))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=6,rawRetained=6,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
