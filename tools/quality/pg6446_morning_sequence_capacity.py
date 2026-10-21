"""Bounded fixed-two owner list allocation proof; no heap exhaustion or native invocation."""
import argparse
import hashlib
import json
import os
import subprocess
import zipfile
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6186_native_ownership_order import methods, instructions, one_call

OLD_SOURCE = '5aa08a26ef867810ddf73349e09a13c6520341b1'
OLD_QSHA = '0a1a830e54043d67f1ace8abb61aedc008eaa3431517719ecabcd8589400f3ff'
CURRENT_QSHA = '8eb15b608718eb0f9eac4a92ccd03db4882a5436876d13c66563beedc3daf3c0'
CLS = 'dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwner'
MAIN = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner.java'


def analyze(blocks, fixed):
    key = next(k for k in blocks if ' void sequence(' in k); code = blocks[key]; ops = instructions(code)
    launches = one_call({'sequence': code}, '$Launch.execute:', 2)
    adds = one_call({'sequence': code}, 'ArrayList.add:', 2)
    ctors = [(at, i, arg) for i, (at, op, arg) in enumerate(ops) if op == 'invokespecial' and 'ArrayList."<init>":' in arg]
    if len(ctors) != 1 or not ctors[0][0] < launches[0][1] < adds[0][1] < launches[1][1] < adds[1][1]:
        raise ValueError('one list allocation before exactly two ordered launch/add pairs')
    one_call({'sequence': code}, '$Completion.execute:'); one_call({'sequence': code}, '$Stop.execute:')
    one_call({'sequence': code}, 'List.copyOf:', 3)
    if fixed:
        if ':(I)V' not in ctors[0][2] or ops[ctors[0][1]-1][1] != 'iconst_2':
            raise ValueError('capacity2 must be allocated before the first returned owner')
    elif ':()V' not in ctors[0][2]:
        raise ValueError('original noarg allocation gap, not already preallocated')
    if any(op in ('putfield', 'putstatic', 'areturn', 'anewarray', 'newarray', 'multianewarray') for _, op, _ in ops):
        raise ValueError('local bounded list, no external alias store or extra array allocation')
    return dict(constructorOffset=ctors[0][0], capacity=2 if fixed else 0,
        launchOffsets=[v[1] for v in launches], addOffsets=[v[1] for v in adds], maximumAdds=2,
        registeredOnlyAfterFirstGrowRisk=not fixed, listStoredInExternalField=False,
        actualHeapFailureInjected=False, nativeOwnershipProven=False)


def jdk_proof():
    raw = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', 'java.util.ArrayList'], text=True)
    blocks = methods(raw)
    noarg = blocks['  public java.util.ArrayList();']; sized = blocks['  public java.util.ArrayList(int);']
    add = blocks['  private void add(E, java.lang.Object[], int);']; clinit = blocks['  static {};']
    if 'DEFAULTCAPACITY_EMPTY_ELEMENTDATA' not in noarg or 'anewarray' not in sized or 'Method grow:' not in add or 'arraylength' not in add:
        raise ValueError('actual pinned JDK empty ctor, eager sized array, capacity-checked grow')
    ops = instructions(clinit)
    stores = [i for i, (_, op, arg) in enumerate(ops) if op == 'putstatic' and 'DEFAULTCAPACITY_EMPTY_ELEMENTDATA:' in arg]
    if len(stores) != 1 or [v[1] for v in ops[stores[0]-2:stores[0]]] != ['iconst_0', 'anewarray']:
        raise ValueError('default backing array really has zero length')
    return dict(jdkReleaseSha256=sha(TC/'jdk-25.0.4/release'),
        relevantMethodsSha256=hashlib.sha256((noarg+sized+add+clinit).encode()).hexdigest(),
        defaultArrayLength=0, positiveConstructorAllocatesBeforeReturn=True, addGrowsOnlyAtCapacity=True)


def record(current=False):
    slot = 'pg6450-morning-sequence-qualification-v1' if current else 'pg6442-morning-diagnostic-qualification-v1'
    public = 'PG6450-morning-sequence-qualification-v1' if current else 'PG6442-morning-diagnostic-qualification-v1'
    qp = BASE/public/'manifest.json'; q = json.loads(qp.read_bytes())
    expected = CURRENT_QSHA if current else OLD_QSHA
    if expected is None or sha(qp) != expected:
        raise ValueError('exact original23 qualification before source-only capacity proof')
    p = W/slot/'manifest.safe.json'
    if q['actualExit'] != 0 or (q['tests'], q['suites'], q['physicalMain']) != (23, 10, 1667) or sha(p) != q['privateManifestSha256']:
        raise ValueError('genuine original23 all source/Jar/XML qualification')
    proof = json.loads(p.read_bytes()); source = q['source']
    if not current and source != OLD_SOURCE:
        raise ValueError('original noarg source fixed')
    run = W/('pg6448-morning-sequence-green-v1' if current else 'pg6440-morning-diagnostic-green-v1')/'source'
    jar = run/'src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
    with zipfile.ZipFile(jar) as z:
        physical = {'batch:'+n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
    if physical != {k: v for k, v in proof['allPhysicalMainSha256'].items() if k.startswith('batch:')} or sha(run/MAIN) != proof['allSourceHashes'][MAIN]:
        raise ValueError('original Batch bytes and source unchanged')
    raw = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jar), CLS], text=True)
    diagnostic = None
    if current:
        old = W/'pg6442-morning-diagnostic-qualification-v1/manifest.safe.json'
        old_public = BASE/'PG6442-morning-diagnostic-qualification-v1/manifest.json'
        if sha(old_public) != OLD_QSHA or sha(old) != json.loads(old_public.read_bytes())['privateManifestSha256']:
            raise ValueError('immutable preceding diagnostic source/class proof')
        before = json.loads(old.read_bytes())
        nested = 'batch:'+CLS.replace('.', '/')+'$CompletionProgress.class'
        if before['allPhysicalMainSha256'][nested] != physical[nested]:
            raise ValueError('previously proved diagnostic class must be physically identical')
        old_jar = W/'pg6440-morning-diagnostic-green-v1/source/src/schubert-nk-batch/target/schubert-nk-batch-0.1.0-SNAPSHOT.jar'
        old_raw = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(old_jar), CLS], text=True)
        previous, now = methods(old_raw), methods(raw)
        if set(previous) != set(now) or any(previous[k] != now[k] for k in previous if ' void sequence(' not in k):
            raise ValueError('all actual outer methods except sequence unchanged after CP-index normalization')
        orderp = BASE/'PG6444-morning-diagnostic-order-v1/manifest.json'
        if sha(orderp) != '2e806bc4138a952baa473e954ecf76853d1be75d120b9e4b3bbd65fda79d485b':
            raise ValueError('immutable diagnostic order, no previous PT/native success import')
        order = json.loads(orderp.read_bytes())
        if order['classSha256'] != physical[nested]:
            raise ValueError('same diagnostic class instructions as independently reviewed')
        cases = json.loads(p.with_name('cases.safe.json').read_bytes())
        refs = [c for c in cases if c['className'] == 'dev.codex.schubert.nk.batch.file.MorningCompletionRetirementTest'
                and c['method'].startswith('completion32600')]
        if len(refs) != 2:
            raise ValueError('two fresh original current diagnostic cases, not old PASS transfer')
        diagnostic = dict(classSha256=physical[nested], priorOrderSha256=sha(orderp),
            allOuterMethodsExceptSequenceEquivalent=True, actualCurrentCaseRefs=refs,
            priorPtOrNativeSuccessImported=False, actualNativeRetentionProven=False)
    value = dict(actualExit=0, source=source, qualificationSha256=sha(qp), classSha256=physical['batch:'+CLS.replace('.', '/')+'.class'],
        sourceSha256=sha(run/MAIN), order=analyze(methods(raw), current), jdk=jdk_proof(),
        diagnosticReauthentication=diagnostic,
        status='FIXED_TWO_SLOTS_ALLOCATED_BEFORE_LAUNCH' if current else 'ORIGINAL_POST_RETURN_FIRST_GROW_GAP',
        productionTestsExecuted=0, buildsIssued=0, vmActions=0, ptAlternativeCompleted=0,
        formalAccepted=False, effortPercent=None, actualHeapFailureMeasured=False)
    os.umask(0o077); out = BASE/('PG6446-sequence-capacity-current-v1' if current else 'PG6446-sequence-capacity-old-gap-v1'); out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, status=value['status'], manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['old', 'current'])
    args = parser.parse_args(); record(args.phase == 'current')
