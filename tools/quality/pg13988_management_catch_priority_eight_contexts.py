"""Eight retained raw warnings/four operand spans/two clauses, public source metadata only."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE = cfg.SOURCE
OUT = data.BASE/'PG13988-management-catch-priority-eight-contexts-v1'
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
RULE = 'AvoidInstanceofChecksInCatchClause'
TARGETS = {
    'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java':('81c29219808b8c38764d7bcd9ec1d1e7fc32a709a158a0399237e7fe5d46cb5c','WBS-P018-05',['PMD-00073','PMD-00074','PMD-00075','PMD-00076']),
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java':('f4b820069ae18d539f6ceb62fd2b2e3b95afe27dafb0bdaf72e35c1fe53a01cf','WBS-P018-06',['PMD-07231','PMD-07232','PMD-07233','PMD-07234']),
}
DESIGN = {'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md':'3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82'}
IDS = {identity for _,_,identities in TARGETS.values() for identity in identities}
REASON = ('The multi-catch handles failed cleanup of a previously captured management owner. '
    'A direct cleanup Error supersedes an ordinary Runtime primary; an already selected primary Error remains first. '
    'The second instanceof prevents replacing the original fatal identity. Non-promoted cleanup contributes only a fixed preallocated secondary diagnostic unless it is the same object. '
    'stopFailure returning an unconfirmed result does not make start succeed: the original failure is thrown. '
    'Splitting or deleting the checks merely to silence PMD can change cleanup/primary order. Actual listener/executor cleanup, suppressed graphs and native owner termination remain unqualified.')

def source_guards(text):
    assert 'if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;' in text
    assert 'if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);' in text
    begin = text.index('    var cleanupDiagnostic =');bind = text.index('    var result = bind(',begin)
    assert begin < bind < text.index('      result.start();',bind)
    catch = text.index('    } catch (RuntimeException | Error failure) {',bind)
    end = text.index('  //',catch)
    body = text[catch:end]
    assert 'result.stopFailure(' in body and 'catch (RuntimeException | Error unconfirmed)' in body
    assert body.rindex('throw failure;') > body.index('closing.ifPresent(')
    assert 'return result;' not in body
    stop = text[text.index('  private Optional<',catch):]
    assert 'stopLock.tryLock(Math.max(0, deadline - System.nanoTime()), TimeUnit.NANOSECONDS)' in stop
    assert 'executor.awaitTermination(' in stop and 'stopLock.unlock();' in stop

def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def rows():
    normal,_ = cfg.normal();hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    for p,pin in DESIGN.items():assert data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT)) == data.sha((data.ROOT/p).read_bytes()) == pin
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result = []
    for path,(pin,owner,identities) in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == pin;source_guards(text)
        ownership = canonical(path,logical);assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        selected = [r for r in facts if r['path']==path and r['rule']==RULE]
        prior = [r for r in original if r['id'] in identities]
        assert len(selected)==len(prior)==4 and Counter(wire(r['attributes']) for r in selected)==Counter(wire(r['attributes']) for r in prior)
        seen = Counter()
        for row in sorted(prior,key=lambda r:r['id']):
            attributes = row['attributes'];key = wire(attributes);matches = [v for v in selected if v['attributes']==attributes]
            assert len(matches)==2 and all(v['sourceSha256']==pin for v in matches) and row['inputSha256']==pin
            start,end,value = span(text,attributes);assert value=='Error'
            prefix = text[max(0,start-32):start]
            operand = 'unconfirmed' if prefix.endswith('unconfirmed instanceof ') else 'failure'
            assert prefix.endswith(operand+' instanceof ')
            result.append(dict(id=row['id'],path=path,source=SOURCE,sourceSha256=pin,rule=RULE,attributes=attributes,originalRowSha256=row['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),typeToken=value,operand=operand,occurrenceOrdinal=seen[key],rawDiagnosticMultiplicity=2,reason=REASON,disposition='FAILURE_PRIORITY_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership));seen[key]+=1
        assert sorted(seen.values())==[2,2]
    assert len(result)==8 and {r['id'] for r in result}==IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();result = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,approvedDesignHashes=DESIGN))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=8,uniqueOperandSpans=4,uniqueCatchClauses=2,rawRetained=8,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
