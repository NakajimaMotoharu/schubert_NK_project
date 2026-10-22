"""Exact ordinary API five fixed outcomes and exception regions; no admission/stop execution."""
import hashlib
import json
import os
import subprocess
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6722_broker_noop_equivalence import tokens
from pg6781_web_stop_result_equivalence import replace_once

OLD='484c92f1ba158a669be3bf68d26b59d8d4622cbd'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java'
BEFORE_PREFIX='''var cleanupDiagnostic = new IllegalStateException(STOP_UNCONFIRMED);
    var result = bind(information, healthy, port, factory);'''
AFTER_PREFIX='''var cleanupDiagnostic = new IllegalStateException(STOP_UNCONFIRMED);
    var closing = Optional.<IllegalStateException>empty();
    var result = bind(information, healthy, port, factory);'''
BEFORE_CATCH='''} catch (RuntimeException | Error failure) {
      try {
        result.close();
      } catch (RuntimeException | Error unconfirmed) {
        if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;
        if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);
      }
      throw failure;
    }'''
AFTER_CATCH='''} catch (RuntimeException | Error failure) {
      try {
        closing = result.stopFailure(CLOSE_TIMEOUT);
      } catch (RuntimeException | Error unconfirmed) {
        if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;
        if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);
      }
      closing.ifPresent(ignored -> failure.addSuppressed(cleanupDiagnostic));
      throw failure;
    }'''
BEFORE_HEADER='void closeWithin(Duration remaining) {'
AFTER_HEADER='''void closeWithin(Duration remaining) {
    var failure = stopFailure(remaining);
    if (failure.isPresent()) throw failure.orElseThrow();
  }
  private Optional<IllegalStateException> stopFailure(Duration remaining) {'''


def expand_to_original(before,after):
    words=tokens(after)
    for first,last in ((AFTER_PREFIX,BEFORE_PREFIX),(AFTER_CATCH,BEFORE_CATCH),('import java.util.Optional;',''),(AFTER_HEADER,BEFORE_HEADER),
      ('if (closed) return Optional.empty();','if (closed) return;'),('closed = true; return Optional.empty();','closed = true;')):
        words=replace_once(words,first,last)
    fixed=tokens('return Optional.of(new IllegalStateException(STOP_UNCONFIRMED));')
    found=[i for i in range(len(words))if words[i:i+len(fixed)]==fixed]
    if len(found)!=5:raise ValueError('exactly five original fixed unknown outcomes')
    for at in reversed(found):words[at:at+len(fixed)]=tokens('throw new IllegalStateException(STOP_UNCONFIRMED);')
    if words!=tokens(before):raise ValueError('all old API state/deadline/interrupt/priority/public tokens unchanged after expansion')
    return dict(expandedTokensSha256=hashlib.sha256(json.dumps(words,separators=(',',':')).encode()).hexdigest(),
      fixedUnknownOutcomes=5,emptyPreparedBeforeBind=True,preallocatedDiagnosticReused=True,oldStateAndExceptionRegionsEqual=True)


def verify_source():
    before=subprocess.check_output(['git','show',OLD+':'+MAIN],cwd=ROOT,text=True)
    return expand_to_original(before,(ROOT/MAIN).read_text())


def main():
    from pg6824_api_management_result_selected import guard
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed source before publishing source proof')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();guard(source)
    value=dict(actualExit=0,source=source,priorSource=OLD,sourcePath=MAIN,sourceSha256=sha(ROOT/MAIN),**verify_source(),
      testsExecuted=0,formalAccepted=False,vmActions=0,ptAlternativeCompleted=0,
      proofScope='SOURCE_STRUCTURE_NOT_DYNAMIC_ALLOCATION_FAILURE_OR_NATIVE_ADMISSION',toolSha256=sha(ROOT/'tools/quality/pg6822_api_stop_result_equivalence.py'))
    out=BASE/'PG6822-api-stop-result-equivalence-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=source,manifestSha256=sha(p),**verify_source())))


if __name__=='__main__':main()
