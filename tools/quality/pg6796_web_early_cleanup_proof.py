"""Pre-acquisition bookkeeping ordering plus exact old cleanup token expansion."""
import json
import os
import subprocess
import pg6781_web_stop_result_equivalence as old
from pg5940_private_lock_compile import ROOT,BASE,sha

EARLY='''var cleanupDiagnostic = new IOException(STOP_UNCONFIRMED);
    var closing = Optional.<IOException>empty();
    var result = bind(information, healthy, port, factory);'''
PREVIOUS='''var cleanupDiagnostic = new IOException(STOP_UNCONFIRMED);
    var result = bind(information, healthy, port, factory);'''


def expand_early(before,after):
    words=old.replace_once(old.tokens(after),EARLY,PREVIOUS)
    words=old.replace_once(words,'} catch (RuntimeException | Error failure) { try { closing = result.stopFailure(java.time.Duration.ofSeconds(30));',
      '} catch (RuntimeException | Error failure) { var closing = Optional.<IOException>empty(); try { closing = result.stopFailure(java.time.Duration.ofSeconds(30));')
    value=old.expand_to_original(before,' '.join(words));value.update(emptyPreparedBeforeBind=True,allocationFailureExecuted=False)
    return value


def verify_source():
    before=subprocess.check_output(['git','show',old.OLD+':'+old.MAIN],cwd=ROOT,text=True)
    return expand_early(before,(ROOT/old.MAIN).read_text())


def main():
    from pg6798_web_correlation_selected import guard
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed source before proof publication')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();guard(source)
    value=dict(actualExit=0,source=source,sourcePath=old.MAIN,sourceSha256=sha(ROOT/old.MAIN),priorBeforeRefactor=old.OLD,
      **verify_source(),testsExecuted=0,formalAccepted=False,vmActions=0,ptAlternativeCompleted=0,
      proofScope='SOURCE_ORDER_AND_EXCEPTION_REGIONS_NOT_DYNAMIC_HEAP_EXHAUSTION',toolSha256=sha(ROOT/'tools/quality/pg6796_web_early_cleanup_proof.py'))
    out=BASE/'PG6796-web-early-cleanup-proof-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),source=source,emptyPreparedBeforeBind=True)))


if __name__=='__main__':main()
