"""Exact SSC335 timing/notification wrapper and unchanged legacy Web stop body; no execution."""
import hashlib
import json
import os
import subprocess
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6722_broker_noop_equivalence import tokens
from pg6781_web_stop_result_equivalence import replace_once
from pg6850_web_deadline_selected import OLD,MAIN,green_guard

BEFORE_LOCK='''stopLock.lock();
    try {
      if (closed.get()) return Optional.empty();
      stopping.set(true);
      promoted.set(false);'''
AFTER_LOCK='''long deadline = System.nanoTime() + remaining.toNanos();
    stopping.set(true);
    promoted.set(false);
    boolean entryInterrupted = Thread.interrupted();
    try {
      try {
        if (!stopLock.tryLock(Math.max(0, deadline - System.nanoTime()), TimeUnit.NANOSECONDS))
          return Optional.of(new IOException(STOP_UNCONFIRMED));
      } catch (InterruptedException notification) {
        Thread.currentThread().interrupt();
        return Optional.of(new IOException(STOP_UNCONFIRMED));
      }
      if (entryInterrupted) Thread.currentThread().interrupt();
      try {
        if (closed.get()) return Optional.empty();'''
BEFORE_AWAIT='executor.awaitTermination(remaining.toNanos(), TimeUnit.NANOSECONDS)'
AFTER_AWAIT='executor.awaitTermination(Math.max(0, deadline - System.nanoTime()), TimeUnit.NANOSECONDS)'
BEFORE_TAIL='''} finally { stopLock.unlock(); } } }'''
AFTER_TAIL='''} finally { stopLock.unlock(); }
    } finally { if (entryInterrupted) Thread.currentThread().interrupt(); } } }'''


def expand(before,after):
    words=tokens(after)
    words=replace_once(words,AFTER_LOCK,BEFORE_LOCK)
    words=replace_once(words,AFTER_AWAIT,BEFORE_AWAIT)
    tail=tokens(AFTER_TAIL)
    if words[-len(tail):]!=tail:raise ValueError('exact outer entry-interrupt restoration and existing unlock')
    words=words[:-len(tail)]+tokens(BEFORE_TAIL)
    if words!=tokens(before):raise ValueError('all other original Web tokens/state/vendor IRQ/exception/owner preparation preserved')
    return dict(legacyTokensSha256=hashlib.sha256(json.dumps(words,separators=(',',':')).encode()).hexdigest(),
      legacyBodyAndOutsideMethodEqual=True,sharedDeadlineForLockAndJoin=True,zeroNeverUnbounded=True,
      stopRequestBeforeLock=True,entryInterruptRestoredBeforeVendor=True,entryInterruptRestoredOnEveryExit=True,
      addedFixedLockUnknownOutcomes=2,vendorPreemptionAdded=False,oldUnstartedUnknownPreserved=True)


def verify_source():
    before=subprocess.check_output(['git','show',OLD+':'+MAIN],cwd=ROOT,text=True)
    return expand(before,(ROOT/MAIN).read_text())


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed source before publishing')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();green_guard(source)
    value=dict(actualExit=0,source=source,priorSource=OLD,sourcePath=MAIN,sourceSha256=sha(ROOT/MAIN),**verify_source(),
      redQualificationSha256='9a9c504cd8712ea90672f29ec603b788ddc897eb887b66194f7a6d10519232f1',testsExecuted=0,
      vmActions=0,formalAccepted=False,ptAlternativeCompleted=0,scope='SOURCE_STRUCTURE_NOT_NATIVE_OR_DYNAMIC_TIMING_QUALIFICATION',
      toolSha256=sha(ROOT/'tools/quality/pg6860_web_deadline_structure.py'))
    out=BASE/'PG6860-web-deadline-structure-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=source,manifestSha256=sha(p))))


if __name__=='__main__':main()
