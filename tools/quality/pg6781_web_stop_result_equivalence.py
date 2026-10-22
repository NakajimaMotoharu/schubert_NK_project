"""Exact state machine/exception-region reverse expansion, not an execution PT oracle."""
import hashlib
import json
import os
import subprocess
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6722_broker_noop_equivalence import tokens
from pg6780_web_management_result_selected import OLD,MAIN

OPEN_OLD='''    } catch (RuntimeException | Error failure) {
      try {
        result.close();
      } catch (IOException closing) {
        failure.addSuppressed(closing);
      } catch (RuntimeException | Error unconfirmed) {
        if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;
        if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);
      }
      throw failure;
    }'''
OPEN_NEW='''    } catch (RuntimeException | Error failure) {
      var closing = Optional.<IOException>empty();
      try {
        closing = result.stopFailure(java.time.Duration.ofSeconds(30));
      } catch (RuntimeException | Error unconfirmed) {
        if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;
        if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);
      }
      closing.ifPresent(failure::addSuppressed);
      throw failure;
    }'''
OLD_HEADER='void closeWithin(java.time.Duration remaining) throws IOException {'
NEW_HEADER='''void closeWithin(java.time.Duration remaining) throws IOException {
    var failure = stopFailure(remaining);
    if (failure.isPresent()) throw failure.orElseThrow();
  }

  private Optional<IOException> stopFailure(java.time.Duration remaining) {'''


def replace_once(words,first,last):
    before=tokens(first);after=tokens(last)
    positions=[i for i in range(len(words))if words[i:i+len(before)]==before]
    if len(positions)!=1:raise ValueError('one exact stop protocol/exception-region boundary')
    at=positions[0];return words[:at]+after+words[at+len(before):]


def expand_to_original(before,after):
    words=tokens(after)
    for first,last in ((OPEN_NEW,OPEN_OLD),('import java.util.Optional;',''),(NEW_HEADER,OLD_HEADER),
      ('if (closed.get()) return Optional.empty();','if (closed.get()) return;'),
      ('closed.set(true); return Optional.empty();','closed.set(true);')):
        words=replace_once(words,first,last)
    converted=tokens('return Optional.of(new IOException(STOP_UNCONFIRMED));')
    positions=[i for i in range(len(words))if words[i:i+len(converted)]==converted]
    if len(positions)!=3:raise ValueError('exactly three original unknown outcomes, none invented')
    for at in reversed(positions):words[at:at+len(converted)]=tokens('throw new IOException(STOP_UNCONFIRMED);')
    if words!=tokens(before):raise ValueError('every old state,lock,deadline,interrupt,mutation,public and unrelated token retained')
    return dict(expandedTokensSha256=hashlib.sha256(json.dumps(words,separators=(',',':')).encode()).hexdigest(),
      outcomeConversions=3,exceptionRegionUnchanged=True,oldStateMachineTokensEqual=True)


def verify_source():
    before=subprocess.check_output(['git','show',OLD+':'+MAIN],cwd=ROOT,text=True)
    return expand_to_original(before,(ROOT/MAIN).read_text())


def main():
    from pg6780_web_management_result_selected import guard
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed source before proof publication')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();guard(source)
    value=dict(actualExit=0,source=source,priorSource=OLD,sourcePath=MAIN,sourceSha256=sha(ROOT/MAIN),**verify_source(),
      proofScope='SOURCE_STRUCTURE_NOT_DYNAMIC_ALLOCATION_FAILURE_TEST',testsExecuted=0,formalAccepted=False,
      vmActions=0,ptAlternativeCompleted=0,toolSha256=sha(ROOT/'tools/quality/pg6781_web_stop_result_equivalence.py'))
    out=BASE/'PG6781-web-stop-result-equivalence-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),**verify_source())))


if __name__=='__main__':main()
