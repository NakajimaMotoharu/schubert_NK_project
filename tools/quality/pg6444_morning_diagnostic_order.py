"""Source-qualified JVM diagnostic protection, never real parent retention or native evidence."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6186_native_ownership_order import methods, instructions, one_call
from pg6442_morning_diagnostic_qualification import original_source

QUALIFICATION_SHA = '0a1a830e54043d67f1ace8abb61aedc008eaa3431517719ecabcd8589400f3ff'
CLS = 'dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwner'
INNER = CLS+'$CompletionProgress'
KEY = 'batch:'+INNER.replace('.', '/')+'.class'
TEST_SHA = '7529b4771bd70c312b798ef9eb9e738dc0bf2ae9017955b3bae5e737ab82ef83'


def analyze(inner, outer):
    failure = next(v for k, v in inner.items() if ' void failure(java.lang.Throwable)' in k)
    phase = next(v for k, v in inner.items() if ' void phase(' in k)
    checked = one_call({'failure': failure}, 'Objects.requireNonNull:')[0][1]
    emit = one_call({'failure': failure}, 'Method emit:')[0][1]
    handlers = re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class (java/lang/RuntimeException|java/lang/Error)\s*$', failure)
    if len(handlers) != 2 or {x[3] for x in handlers} != {'java/lang/RuntimeException', 'java/lang/Error'}:
        raise ValueError('both unchecked diagnostic types must be protected')
    spans = {(int(a), int(b), int(c)) for a, b, c, _ in handlers}
    if len(spans) != 1:
        raise ValueError('same exact diagnostic protected span and handler')
    first, last, target = next(iter(spans))
    if not checked < first <= emit < last <= target:
        raise ValueError('nonnull boundary outside; complete emit invocation inside protection')
    ops = instructions(failure)
    protected = [(at, op, arg) for at, op, arg in ops if first <= at < last]
    if any(op.startswith('invoke') and 'Method emit:' not in arg for _, op, arg in protected):
        raise ValueError('classification and emit only, no extra resource action')
    tail = [op for at, op, _ in ops if at >= target]
    if len(tail) != 2 or not tail[0].startswith('astore') or tail[1] != 'return':
        raise ValueError('diagnostic handler must return, not throw or run callbacks')
    one_call({'phase': phase}, 'Method emit:')
    if 'Exception table:' in phase:
        raise ValueError('normal phase failures must not become best effort')
    calls = one_call(outer, 'CompletionProgress.failure:')
    name, at, index = calls[0]; owner_ops = instructions(outer[name])
    if index+1 >= len(owner_ops) or owner_ops[index+1][1] != 'invokestatic' or 'Method retain:' not in owner_ops[index+1][2]:
        raise ValueError('original completion handler must go directly from failure to retain')
    return dict(nullCheckOffset=checked, emitOffset=emit, protectedStart=first, protectedEnd=last,
        diagnosticHandler=target, diagnosticHandlerOnlyStoresAndReturns=True,
        outerMethod=name, originalFailureCallOffset=at, nextRetainOffset=owner_ops[index+1][0],
        normalPhaseFailureStillPropagates=True, actualNativeRetentionProven=False)


def read(root, inner=True):
    jar = root/'src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    return jar, subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jar), INNER if inner else CLS], text=True)


def main():
    source = original_source(); qp = BASE/'PG6442-morning-diagnostic-qualification-v1/manifest.json'
    if QUALIFICATION_SHA is None or sha(qp) != QUALIFICATION_SHA:
        raise ValueError('pin original23 qualification first, no begin or prior success')
    q = json.loads(qp.read_bytes()); private = W/'pg6442-morning-diagnostic-qualification-v1/manifest.safe.json'
    if q['source'] != source or q['actualExit'] != 0 or (q['tests'], q['suites'], q['physicalMain']) != (23, 10, 1667) or sha(private) != q['privateManifestSha256']:
        raise ValueError('same original23/all8511667/sixJar')
    proof = json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('every current Main still fixed')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all original Main/Test/gates unchanged')
    jar, inner_text = read(W/'pg6440-morning-diagnostic-green-v1/source')
    _, outer_text = read(W/'pg6440-morning-diagnostic-green-v1/source', False)
    with zipfile.ZipFile(jar) as z:
        actual = {'batch:'+n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
    if actual != {k: v for k, v in proof['allPhysicalMainSha256'].items() if k.startswith('batch:')}:
        raise ValueError('all original Batch Jar bytes still qualified')
    order = analyze(methods(inner_text), methods(outer_text))
    cases = json.loads(private.with_name('cases.safe.json').read_bytes())
    names = {'completion326001FailureDiagnosticCannotThrowBeforeOwnerRetention', 'completion326002NormalPhaseDiagnosticStillPropagatesIdenticalFailure'}
    refs = [c for c in cases if c['className'] == 'dev.codex.schubert.nk.batch.file.MorningCompletionRetirementTest' and c['method'] in names]
    test = ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningCompletionRetirementTest.java'
    if len(refs) != 2 or {c['method'] for c in refs} != names or sha(test) != TEST_SHA:
        raise ValueError('two actual fixed independent cases, not matrix as extra PT')
    counters = proof['allActualCounters'][KEY]
    four = {k: counters[k] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH') if k in counters}
    if set(four) != {'LINE', 'METHOD', 'CLASS', 'BRANCH'} or any(v['missed'] != 0 or v['covered'] <= 0 for v in four.values()):
        raise ValueError('actual diagnostic class four counters, no missing/zero normalization')
    value = dict(actualExit=0, source=source, originalQualificationSha256=sha(qp), allSourceClassQualified=True,
        classSha256=actual[KEY], javapSha256=hashlib.sha256(inner_text.encode()).hexdigest(),
        outerJavapSha256=hashlib.sha256(outer_text.encode()).hexdigest(), order=order,
        actualIndependentCaseRefs=refs, fixedIndependentTestSha256=TEST_SHA, actualClassFourCounters=four,
        testsExecuted=0, buildsIssued=0, vmActions=0, formalAccepted=False, F03Accepted=False,
        ptAlternativeCompleted=0, newAcceptedLeaves=0, effortPercent=None,
        residual=['normal parent/Root resource retention and native lifetime not proven',
                  'whole/new-source static/global/CHR/451 quality still separate'])
    os.umask(0o077); out = BASE/'PG6444-morning-diagnostic-order-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, actualFour=four, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
