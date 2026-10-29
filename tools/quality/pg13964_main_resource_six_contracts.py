"""Six exact public-source ownership references; no target execution or warning suppression."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE = cfg.SOURCE
OUT = data.BASE/'PG13964-main-resource-six-contracts-v1'
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
TARGETS = {
    'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorProcess.java':('73a31b3721e997fde1486a4dd0d76e074a5224420b52763c76a1dcc0b7618ff5','WBS-P004-04',{('load','material'):'PMD-00154',('close','material'):'PMD-00155'}),
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration.java':('f0d5b21a34e7e9d5879663ee49e4645d34115aef60b2d3119594cf9c424a731f','WBS-P018-01',{'current':'PMD-02813'}),
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java':('8d04ab28261de2e41ccc24790d732922f02c823aad5c0f374d6040e99cbe9a7e','WBS-P017-11',{'query':'PMD-03344','values':'PMD-03345'}),
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/BackupArchiveProcess.java':('a70de6c02dec8e284d145d5323d11c9c50c94a7078769136951d4f286ee7d743','WBS-P017-03',{'owned':'PMD-02994'}),
}
DEPENDENCIES = {
    'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorAesCredential.java':'653122ba99e00ebd2b29eb2d1d406f79e370d1f577b4cc212a411535439c7bf8',
    'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java':'639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf',
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/JdbcResourceFailures.java':'f4cff9bb43cacfde5be699fd61d4e25526523d5ef5e478aa88dcbb8bdde6928a',
}
DESIGN = {
    'documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md':'2bc99fd66ca1121a1ab4ae44e97aab96b52d4cf4c8145f6a425f89c7b07ce774',
    'documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md':'d861735e91a6930bbf239937deda29f3675fbf50817953a61e07c0255387fa66',
    'documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md':'b721e6f7d0ee3f17cfe1a2d38512623814b0a10c8a7ad8ae737c62eeda192195',
}
REASONS = {
    'PMD-00154':'material is the identical value returned in source.load Optional, transferred into the operation-local precreated EnumMap before copyKey. OwnedKeys is outer TWR before load; later missing/invalid key, copy, codec or inspector failure closes that owner. The alias must not close immediately because version/cipher setup still borrows it. Real key loading, copy erasure timing and held response-codec closure remain runtime pending; no credential is read here.',
    'PMD-00155':'material iterates values already owned by the same operation-local materials map, not a fresh acquisition. OwnedKeys.close wipes all copies, invokes each material close, then clears both maps. InspectorAesCredential.close uses its state lock and wipes before setting closed. This is explicit terminal release of each borrowed loop alias, not a missing local TWR. No concurrent/actual private-key qualification is claimed.',
    'PMD-02813':'current borrows held.getLast from enclosing ResourceScope ownership. Each recursive child is separately acquired and released by ResourceScope while ancestors stay in the held list for pre/post inode checks. The root owner encloses the whole walk. Closing current locally would duplicate child/root ownership and invalidate ancestors. Public file stream is independently acquire/close scoped. No actual traversal, inode identity or successful FD close is proved.',
    'PMD-03344':'query aliases presentRead(statement), the same nonnull PreparedStatement already captured before the inner try. The outer finally closes statement once after row scope, including early return/error. Borrowed connection/transaction are not owned here; manual close retains JdbcResourceFailures precedence. No SQL or actual DB result is executed by the review.',
    'PMD-03345':'values aliases presentRead(rows), the same nullable-acquired ResultSet protected by its finally. rows close occurs before statement close and before a pending Optional result can return; known SQL/null data are normalized without treating unknown provider failure as success. The alias must not be separately closed. Dynamic JDBC close/graph behavior remains pending.',
    'PMD-02994':'owned is only an OutputStream cast of the stream previously captured by StdIoOwner, which is already enclosed in ResourceScope before writeAndClose. The method writes through the alias then calls the owner close; write failure reaches enclosing release. The closed flag records one release attempt and is set before provider close; this static alias reference does NOT prove successful close or resolve uncertain stream outcomes. Pipeline process terminal/quarantine is a separate owner contract; real pipeline/stdin/termination/borrowed frame effects remain unqualified.',
}
IDS = set(REASONS)

def source_guards(path, text):
    if path.endswith('/InspectorProcess.java'):
        assert 'try (var keys = new OwnedKeys()) {' in text
        assert 'var material = loaded.orElseThrow();' in text
        assert text.index('materials.put(') < text.index('copies.put(id, material.copyKey());')
        assert 'for (var material : materials.values()) material.close();' in text
        assert text.index('for (byte[] copy : copies.values()) Arrays.fill(copy, (byte) 0);') < text.index('for (var material : materials.values()) material.close();') < text.index('copies.clear();') < text.index('materials.clear();')
        load = text[text.index('    void load('):text.index('    Optional<String> version(')]
        assert 'material.close(' not in load
    elif path.endswith('/CaddyPublicConfiguration.java'):
        assert 'var current = held.getLast();' in text
        assert 'List.of(directory)' in text and 'var next = new ArrayList<>(held);' in text and 'next.add(child);' in text
        assert '() -> current.openExistingChild(segments.get(index)),' in text
        assert text.count('OwnedTransferDirectory::close,') == 2
        assert 'return walk(root, morning, fixed, ca, List.copyOf(next), segments, index + 1);' in text
        assert 'current.close(' not in text and 'java.io.InputStream::close,' in text
        assert text.index('var before =') < text.index('var after =') < text.index('requireStableDirectory(before, after);')
    elif path.endswith('/ExpiryAuditRepository.java'):
        assert 'var query = presentRead(statement);' in text and 'var values = presentRead(rows);' in text
        begin = text.index('  public Optional<Snapshot> read(');end = text.index('  /** SSC310:',begin);body = text[begin:end]
        assert body.count('rows.close();') == body.count('statement.close();') == 1
        assert body.index('rows.close();') < body.index('statement.close();')
        assert 'if (JdbcResourceFailures.replace(rowFailure, secondary)) throw secondary;' in body
        assert 'if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;' in body
        assert all(value not in body for value in ['query.close(', 'values.close(', 'connection.close(', 'connection.commit(', 'connection.rollback('])
    else:
        assert path.endswith('/BackupArchiveProcess.java')
        assert 'inputs.getFirst().writeAndClose(input);' in text and 'StdIoOwner::close,' in text
        assert 'var owned = (OutputStream) Objects.requireNonNull(stream, "admitted stdin");' in text
        body = text[text.index('    void writeAndClose('):text.index('  /** All callbacks')]
        assert body.index('owned.write(bytes);') < body.index('      close();')
        assert body.index('closed = true;') < body.index('BackupArchiveProcess.close(stream);')
        assert 'owned.close(' not in body
        assert 'ResourceScope.acquire(' in text and 'terminal::close,' in text

def rows():
    normal,_ = cfg.normal();hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    for p,pin in DEPENDENCIES.items():assert data.sha((data.ROOT/p).read_bytes()) == hashes[p] == pin
    for p,pin in DESIGN.items():
        public = subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT)
        assert data.sha(public) == data.sha((data.ROOT/p).read_bytes()) == pin
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result = []
    for path,(pin,owner,fields) in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == pin;source_guards(path,text)
        ownership = canonical(path,logical);assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        selected = [r for r in facts if r['path'] == path and r['rule'] == 'CloseResource'];assert len(selected) == len(fields)
        for row in selected:
            attributes = row['attributes'];variable = attributes['variable'];identity = fields[(attributes['method'],variable)] if (attributes['method'],variable) in fields else fields[variable];old, = [r for r in original if r['id'] == identity]
            assert old['path'] == path and old['rule'] == row['rule'] and old['attributes'] == attributes and old['inputSha256'] == row['sourceSha256'] == pin
            start,end,value = span(text,attributes);assert value == variable
            result.append(dict(id=identity,path=path,source=SOURCE,sourceSha256=pin,rule=row['rule'],variable=variable,attributes=attributes,originalRowSha256=old['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),reason=REASONS[identity],disposition='OWNERSHIP_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership))
    assert len(result) == 6 and {r['id'] for r in result} == IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();result = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,dependencySourceHashes=DEPENDENCIES,approvedDesignHashes=DESIGN))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=6,rawRetained=6,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
