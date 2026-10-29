"""Seventeen retained raw JMS type-priority references; public source/XML metadata only."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE=cfg.SOURCE
OUT=data.BASE/'PG14020-batch-transaction-type-priority-twenty-eight-contexts-v1'
MEASURED=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
RULE='AvoidInstanceofChecksInCatchClause'
TARGETS=json.loads("{\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/backup/BackupCommitService.java\":[\"c57ed4ca018b637f6c5aaa683da533489dfbf24c316dc0e806b5948e88aea1b4\",\"WBS-P017-05\",[\"PMD-02703\",\"PMD-02704\",\"PMD-02705\",\"PMD-02706\",\"PMD-02707\",\"PMD-02708\",\"PMD-02709\",\"PMD-02710\",\"PMD-02711\",\"PMD-02712\",\"PMD-02713\",\"PMD-02714\"]],\"src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/cleanup/StepCleanupService.java\":[\"d596b52c53b09455e9c45003b8dcd8c494f835c456b84f6384d52f450edf2bc9\",\"WBS-P017-07\",[\"PMD-02756\",\"PMD-02757\",\"PMD-02758\",\"PMD-02759\",\"PMD-02760\",\"PMD-02761\",\"PMD-02762\",\"PMD-02763\",\"PMD-02764\",\"PMD-02765\",\"PMD-02766\",\"PMD-02767\",\"PMD-02768\",\"PMD-02769\",\"PMD-02770\",\"PMD-02771\"]]}")
DESIGN={
 'documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md':'b721e6f7d0ee3f17cfe1a2d38512623814b0a10c8a7ad8ae737c62eeda192195',
 'documents/300_SS/330_データ・ファイル/331_DB物理・DDL・index・権限設計.md':'7f6e0430a38769dad5d94ed8d95faaab124f4bb86246c478feee5b50ffca26d5',
}
IDS={v for _,_,ids in TARGETS.values() for v in ids}

def reason(path,method):
    assert method in ('complete','transaction')
    return ('SS341 section6.6 BUG193/YKT152: after failed owned transaction setup/body/commit, cleanup attempts rollback then autoCommit restoration. '
      'An unknown Runtime/NPE/Error primary keeps its original identity with one newly fixed redacted secondary, never raw self-suppression. '
      'A known SQL/Repository'+('/CleanupStopped' if method=='transaction' else '')+' primary yields to an unknown cleanup Runtime/Error; known cleanup remains fixed database failure. '
      'The instanceof clauses implement these exception category boundaries rather than ordinary instanceof dispatch. '
      +('A durable committed chunk is never rolled back after later owner check fails. ' if method=='transaction' else '')+
      'Caller still disposes the borrowed connection after failure; source review is not DB mutation, rollback/commit confirmation, actual backup/lock/owner authentication or dynamic exception proof.')
GUARDS={
 'BackupCommitService.java':[
  'catch (SQLException | RuntimeException | Error failure)',
  'connection.rollback();','connection.setAutoCommit(true);',
  'if (failure instanceof Error','|| (failure instanceof RuntimeException',
  '&& !(failure instanceof BatchRepositoryException)))',
  'failure.addSuppressed(new BatchRepositoryException());',
  'if (cleanupFailure instanceof Error fatal) throw fatal;',
  'if (cleanupFailure instanceof RuntimeException',
  '&& !(cleanupFailure instanceof BatchRepositoryException)) throw cleanupFailure;'],
 'StepCleanupService.java':[
  'if (committed) throw failure;',
  'c.rollback();','c.setAutoCommit(true);',
  'if (failure instanceof Error','|| (failure instanceof RuntimeException',
  '&& !(failure instanceof BatchRepositoryException)',
  '&& !(failure instanceof CleanupStoppedException)))',
  'failure.addSuppressed(new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE));',
  'if (cleanupFailure instanceof Error fatal) throw fatal;',
  'if (cleanupFailure instanceof RuntimeException',
  '&& !(cleanupFailure instanceof BatchRepositoryException)',
  '&& !(cleanupFailure instanceof CleanupStoppedException)) throw cleanupFailure;'],
}
def source_guards(path,text):
    for phrase in GUARDS[path.rpartition('/')[2]]:assert phrase in text
    if path.endswith('BackupCommitService.java'):
        assert text.index('connection.rollback();')<text.index('connection.setAutoCommit(true);')
    else:
        assert text.index('c.commit();')<text.index('committed = true;')<text.index('if (committed) throw failure;')<text.index('c.rollback();')<text.index('c.setAutoCommit(true);')

def wire(value):return json.dumps(value,sort_keys=True,separators=(',',':'))

def rows():
    normal,_=cfg.normal();hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    for p,pin in DESIGN.items():assert data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT))==data.sha((data.ROOT/p).read_bytes())==pin
    measured=data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1])
    assert measured['actualExit']==0 and measured['analysisComplete'] and not measured['processingErrors']
    facts=data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result=[]
    for path,(pin,owner,identities) in TARGETS.items():
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==hashes[path]==pin;source_guards(path,text)
        ownership=canonical(path,logical);assert ownership['canonicalOwner']==ownership['canonicalCostOwner']==owner
        selected=[r for r in facts if r['path']==path and r['rule']==RULE]
        prior=[r for r in original if r['id'] in identities]
        assert len(selected)==len(prior)==len(identities) and Counter(wire(r['attributes']) for r in selected)==Counter(wire(r['attributes']) for r in prior)
        seen=Counter()
        for row in sorted(prior,key=lambda r:r['id']):
            attributes=row['attributes'];key=wire(attributes);matches=[v for v in selected if v['attributes']==attributes]
            assert all(v['sourceSha256']==pin for v in matches) and row['inputSha256']==pin
            start,end,value=span(text,attributes);assert value in ('Error','RuntimeException','BatchRepositoryException','CleanupStoppedException')
            anchor=text.rfind('catch (',0,start);assert anchor>=0
            result.append(dict(id=row['id'],path=path,source=SOURCE,sourceSha256=pin,rule=RULE,attributes=attributes,originalRowSha256=row['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),typeToken=value,catchAnchor=anchor,occurrenceOrdinal=seen[key],rawDiagnosticMultiplicity=len(matches),reason=reason(path,attributes['method']),disposition='TYPE_PRIORITY_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership))
            seen[key]+=1
        assert all(seen[k]==len([v for v in selected if wire(v['attributes'])==k]) for k in seen)
    assert len(result)==28 and {r['id'] for r in result}==IDS
    assert len({(r['path'],r['spanStart'],r['spanEndExclusive']) for r in result})==14
    assert len({(r['path'],r['catchAnchor']) for r in result})==4
    return sorted(result,key=lambda r:r['id'])

if __name__=='__main__':
    invocation=capture(__file__);assert not OUT.exists();result=rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,approvedDesignHashes=DESIGN,historicalReviewNotTransferred='1364 old source; current references only'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=28,uniqueOperandSpans=14,uniqueCatchClauses=4,rawRetained=28,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
