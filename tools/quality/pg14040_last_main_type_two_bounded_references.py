"""Last two bounded public source references, no whole Java Unicode parser or runtime proof."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE=cfg.SOURCE
OUT=data.BASE/'PG14040-last-main-type-two-bounded-references-v1'
MEASURED=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
RULE='AvoidInstanceofChecksInCatchClause'
TARGETS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionService.java':('d303f5a79375d69bbc4f45c91d4ab74bd5744c40baafe45f6cbe8beb692ffaa2','WBS-P011-02',['PMD-00048']),
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupArtifactVerifier.java':('244c5b3542468956bbe0fef5ae2054f8deb509d4d5db537e4e9b4d2ba9727cbf','WBS-P017-05',['PMD-02778']),
}
DESIGN={
 'documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md':'7fc9bb837b9669f301c4c8d1b0b93ea1d680fd6c30e34b7f754e5210beb3765b',
 'documents/300_SS/330_データ・ファイル/331_DB物理・DDL・index・権限設計.md':'7f6e0430a38769dad5d94ed8d95faaab124f4bb86246c478feee5b50ffca26d5',
 'documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md':'b721e6f7d0ee3f17cfe1a2d38512623814b0a10c8a7ad8ae737c62eeda192195',
}
IDS={'PMD-00048','PMD-02778'}
GUARDS={
 'QuestionSubmissionService.java':['for (int attempt = 0; attempt < 3; attempt++)','Savepoint before = connection.setSavepoint();','TemporaryInfrastructureException.preserveFatal(failure);','if (!(failure instanceof PSQLException postgres) || !"23505".equals(failure.getSQLState()))','if (error == null || !"uq_questions_receipt_id".equals(error.getConstraint()))','connection.rollback(before);','connection.releaseSavepoint(before);','throw new SQLException("receipt identity collision budget exhausted", "40001");'],
 'BackupArtifactVerifier.java':['if (force != null && failure instanceof StorageIoException storage)','throw new StorageIoException(storage.reason());','throw unavailable();','Arrays.fill(buffer, (byte) 0);','Arrays.fill(canonical, (byte) 0);','lock.unlock();'],
}
def reason(path,method):
    if method=='insertQuestion':
        return 'Question insert permits bounded savepoint retry only for driver-typed PostgreSQL23505 plus the exact receipt unique constraint, after fatal graph classification. Other SQL/state/constraint/null metadata propagates failure; ownership/token failures are not retried as receipt collisions. This raw reference uses the unchanged no-Unicode-escape prefix through source line417, not a whole-file Java Unicode translation claim. Actual DB/savepoint/retry/graph remains unqualified.'
    assert method=='verifyAt'
    return 'Backup verifyAt checked failure preserves a typed StorageIoException reason only on the existing force-enabled durability path; otherwise fixed unavailable. The instanceof is necessary before reason access in the IO/iterator/unsupported union, while buffers and lock release remain finally-owned. No actual artifact/root/force/verification/Backup/key/native result follows from this static reason.'
def source_guards(path,text):
    for phrase in GUARDS[path.rpartition('/')[2]]:assert phrase in text
    if path.endswith('QuestionSubmissionService.java'):
        begin=text.index('  private QuestionSubmitResponseData insertQuestion(')
        body=text[begin:text.index('  private Accepted read(',begin)]
        assert body.index('TemporaryInfrastructureException.preserveFatal(failure);')<body.index('failure instanceof PSQLException')<body.index('error.getConstraint()')<body.index('connection.rollback(before);')
    else:
        begin=text.index('      } catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure)',text.index('  private BundleSnapshot verifyAt('))
        body=text[begin:text.index('  private Metadata directory(',begin)]
        assert body.index('force != null && failure instanceof StorageIoException')<body.index('throw new StorageIoException(storage.reason());')<body.index('Arrays.fill(buffer, (byte) 0);')<body.index('lock.unlock();')
def bounded_span(path,text,attributes):
    if path.endswith('QuestionSubmissionService.java'):
        assert attributes['beginline']==attributes['endline']=='417'
        prefix=''.join(text.splitlines(keepends=True)[:417])
        assert chr(92)+'u' not in prefix and chr(92)+'u' in text[len(prefix):]
        assert data.sha(prefix.encode())=='382bb161498bbd3d20250df0029f0241f5980ab866aba1a345334a19faedea52'
        result=span(prefix,attributes)
        assert result[2]=='PSQLException' and text[result[0]:result[1]]==result[2]
        return result,dict(mode='ORIGINAL_NO_ESCAPE_PREFIX_THROUGH_SELECTED_LINE',prefixLines=417,prefixSha256=data.sha(prefix.encode()),suffixUnicodeEscapesNotTranslated=True,wholeJavaUnicodeTranslationValidated=False,spanProofIsPrefixOnly=True)
    return span(text,attributes),dict(mode='ORIGINAL_ORDINARY_LF_FULL_SOURCE',wholeJavaUnicodeTranslationValidated=False,spanProofIsPrefixOnly=False)
def rows():
    normal,_=cfg.normal();hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    for p,pin in DESIGN.items():assert data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT))==data.sha((data.ROOT/p).read_bytes())==pin
    measured=data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1])
    facts=data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    old=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result=[]
    for path,(pin,owner,identities) in TARGETS.items():
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==hashes[path]==pin;source_guards(path,text)
        ownership=canonical(path,logical);assert ownership['canonicalOwner']==ownership['canonicalCostOwner']==owner
        selected=[r for r in facts if r['path']==path and r['rule']==RULE]
        prior=[r for r in old if r['id'] in identities]
        assert len(selected)==len(prior)==1 and selected[0]['attributes']==prior[0]['attributes']
        row=prior[0];assert row['inputSha256']==selected[0]['sourceSha256']==pin
        (start,end,value),scope=bounded_span(path,text,row['attributes'])
        method=row['attributes']['method']
        declaration='catch (SQLException failure)' if method=='insertQuestion' else 'catch (IOException | DirectoryIteratorException | UnsupportedOperationException failure)'
        method_start=text.index('  private QuestionSubmitResponseData insertQuestion(') if method=='insertQuestion' else text.index('  private BundleSnapshot verifyAt(')
        anchor=text.index(declaration,method_start);assert anchor<start
        result.append(dict(id=row['id'],path=path,source=SOURCE,sourceSha256=pin,rule=RULE,attributes=row['attributes'],originalRowSha256=row['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),typeToken=value,coordinateScope=scope,catchAnchor=anchor,occurrenceOrdinal=0,rawDiagnosticMultiplicity=1,reason=reason(path,method),disposition='BOUNDED_TYPE_REASON_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership))
    assert len(result)==2 and {r['id'] for r in result}==IDS
    return sorted(result,key=lambda r:r['id'])
if __name__=='__main__':
    invocation=capture(__file__);assert not OUT.exists();result=rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,approvedDesignHashes=DESIGN))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=2,uniqueOperandSpans=2,uniqueCatchClauses=2,rawRetained=2,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False,wholeJavaUnicodeTranslationValidated=False,existingSpanToolUnmodified=True))
    print(data.sha((OUT/'manifest.json').read_bytes()))
