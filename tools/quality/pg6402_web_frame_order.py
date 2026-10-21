"""Qualified original JVM: both finally clones retain callbacks; no fabricated branch counter."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from collections import defaultdict
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6186_native_ownership_order import methods, instructions, one_call
from pg6084_web_factory_order import narrow_or_wide_literal_body
from pg6263_branchless_original import no_branches
from classfile_field_flags import fields
from pg6414_web_frame_pending_qualification import original_source

QUALIFICATION_SHA = 'f214986209f003c92248644f55e617042af273ab6b652a2e753dffceda30498f'
CLS = 'dev.codex.schubert.nk.web.bootstrap.WebRuntimeExecution'
KEY = 'web:'+CLS.replace('.', '/')+'.class'


def local_slot(op, argument, prefix):
    if op == prefix:
        return int(argument.strip())
    if op.startswith(prefix+'_'):
        return int(op.removeprefix(prefix+'_'))
    raise ValueError('exact reference-local opcode, no inferred liveness')


def receiver(ops, index):
    if index <= 0:
        raise ValueError('explicit call receiver required')
    _, op, argument = ops[index-1]
    return argument if op == 'getstatic' else ('local:'+str(local_slot(op, argument, 'aload')))


def analyze(blocks):
    code = next(v for k, v in blocks.items() if ' execute(' in k)
    ops = instructions(code)
    backward = [(at, int(argument.strip())) for at, op, argument in ops if op == 'goto' and int(argument.strip()) < at]
    if len(backward) != 2:
        raise ValueError('normal and exceptional finally each owns one retaining loop')
    close_calls = one_call({'execute': code}, 'WebRuntimeExecution$Io.run:', 3)
    one_call({'execute': code}, 'WebRuntimeExecution$Start.run:')
    one_call({'execute': code}, 'Objects.requireNonNull:', 4)
    one_call({'execute': code}, 'Reference.reachabilityFence:', 10)
    grouped = defaultdict(list)
    for first, last, handler, kind in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class (java/io/IOException|java/lang/RuntimeException|java/lang/Error)\s*$', code):
        grouped[int(handler)].append((int(first), int(last), kind))
    if len(grouped) != 2 or any({kind for _, _, kind in rows} != {'java/io/IOException', 'java/lang/RuntimeException', 'java/lang/Error'} or len(rows) != 3 for rows in grouped.values()):
        raise ValueError('both close sites catch all specified IO/Runtime/Error types')
    reviews = []
    for back, target in backward:
        region = [(i, at, op, arg) for i, (at, op, arg) in enumerate(ops) if target <= at <= back]
        if any(op in ('return', 'areturn', 'athrow', 'new', 'newarray', 'anewarray', 'multianewarray', 'invokedynamic') for _, _, op, _ in region):
            raise ValueError('no owner unwind or new holding allocation in either loop')
        ticks = [(i, at) for i, at, op, arg in region if op.startswith('invoke') and 'Runnable.run:' in arg]
        if len(ticks) != 1 or 'Field UNKNOWN_INTERVAL:' not in receiver(ops, ticks[0][0]):
            raise ValueError('one prepared protected finite tick per loop')
        fences = [(i, at) for i, at, op, arg in region if op.startswith('invoke') and 'Reference.reachabilityFence:' in arg]
        if len(fences) != 5 or not ticks[0][1] < min(at for _, at in fences):
            raise ValueError('all five callback/failure fences after each finite tick')
        slots = [local_slot(ops[i-1][1], ops[i-1][2], 'aload') for i, _ in fences]
        if slots[:4] != [0, 1, 2, 3] or slots[4] <= 3:
            raise ValueError('retain each original callback and this close failure')
        diagnostic = [(i, at) for i, (at, op, arg) in enumerate(ops) if at < target and op.startswith('invoke') and 'Runnable.run:' in arg]
        if not diagnostic or 'Field UNKNOWN_DIAGNOSTIC:' not in receiver(ops, diagnostic[-1][0]):
            raise ValueError('prepared fixed diagnostic immediately precedes retention')
        candidates = [(handler, rows) for handler, rows in grouped.items() if handler < diagnostic[-1][1]
                      and local_slot(next(op for at, op, _ in ops if at == handler), next(arg for at, _, arg in ops if at == handler), 'astore') == slots[4]]
        if len(candidates) != 1:
            raise ValueError('same exact caught UNKNOWN occupies fifth fenced slot')
        handler, rows = candidates[0]
        owned_close = [at for _, at, _ in close_calls if all(first <= at < last for first, last, _ in rows)]
        if len(owned_close) != 1:
            raise ValueError('one guarded close attempt, never retry')
        before = [(i, at) for i, (at, op, arg) in enumerate(ops) if at < owned_close[0] and op.startswith('invoke') and 'Runnable.run:' in arg]
        if not before or receiver(ops, before[-1][0]) != 'local:2':
            raise ValueError('original nonthrowing stop notification precedes close')
        reviews.append(dict(closeOffset=owned_close[0], closeHandler=handler, diagnosticOffset=diagnostic[-1][1],
            tickOffset=ticks[0][1], fenceOffsets=[at for _, at in fences], heldLocalSlots=slots, loopTarget=target,
            backedge=back, closeAttempts=1, loopReturnThrowAllocations=0))
    if len({r['closeHandler'] for r in reviews}) != 2:
        raise ValueError('distinct normal/exceptional finally close frames')
    return reviews


def read(root):
    jar = root/'src/schubert-nk-web/target/schubert-nk-web-0.1.0-SNAPSHOT.jar'
    text = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jar), CLS], text=True)
    return jar, text


def main():
    source = original_source(); qp = BASE/'PG6414-web-frame-pending-qualification-v1/manifest.json'
    if QUALIFICATION_SHA is None or sha(qp) != QUALIFICATION_SHA:
        raise ValueError('bind genuine original26 qualification before final review publication')
    q = json.loads(qp.read_bytes()); private = W/'pg6414-web-frame-pending-qualification-v1/manifest.safe.json'
    if not (q['source'] == source and q['actualExit'] == 0 and (q['tests'], q['suites'], q['physicalMain']) == (26, 12, 1667)
            and sha(private) == q['privateManifestSha256']):
        raise ValueError('genuine original26/all8511667/sixJar qualification')
    proof = json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all original source/Test/gates fixed')
    old_path = BASE/'PG6386-current4052-cases/qualification.json'
    if sha(old_path) != '5b42051bf7ca435c44e3f7caa2fb0fca245faae9c32c3fda4b508ee40a4314b4':
        raise ValueError('immutable previous whole physical map')
    old_map = json.loads(old_path.read_bytes())['allPhysicalMainSha256']; current = proof['allPhysicalMainSha256']
    if set(old_map) != set(current) or {k for k in current if current[k] != old_map[k]} != {KEY}:
        raise ValueError('only one changed physical class, other1666 identical')
    jar, text = read(W/'pg6412-web-frame-pending-selected-v1/source')
    _, before = read(W/'pg6382-web-fatal-callback-retry-v1/source')
    left, right = methods(before), methods(text)
    if not set(left) <= set(right) or len(set(right)-set(left)) != 2 or not any(' diagnoseUnknown(' in k for k in set(right)-set(left)) or '  static {};' not in right:
        raise ValueError('original descriptors/visibility preserved, only private diagnostic/clinit added')
    constructor = next(k for k in left if k.startswith('  private ') and CLS+'(' in k)
    if narrow_or_wide_literal_body(left[constructor]) != narrow_or_wide_literal_body(right[constructor]):
        raise ValueError('original empty private utility constructor unchanged')
    with zipfile.ZipFile(jar) as z:
        actual = {'web:'+n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
        flags = fields(z.read(CLS.replace('.', '/')+'.class'))
    if actual != {k: v for k, v in current.items() if k.startswith('web:')}:
        raise ValueError('every original Web Jar class still qualified')
    if set(flags) != {b'UNKNOWN_DIAGNOSTIC', b'UNKNOWN_INTERVAL'} or any(f['flags'] != 0x1a for f in flags.values()):
        raise ValueError('exact two private static final prepared policies')
    clinit = right['  static {};']
    one_call({'clinit': clinit}, 'ServiceProcessResources.unknownReleaseObservationPolicy:')
    diagnostic = next(v for k, v in right.items() if ' diagnoseUnknown(' in k)
    one_call({'diagnostic': diagnostic}, 'PrintStream.println:')
    if diagnostic.count('String WEB cleanup unconfirmed') != 1:
        raise ValueError('fixed existing diagnostic only')
    table = re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class java/lang/(RuntimeException|Error)\s*$', diagnostic)
    at = one_call({'diagnostic': diagnostic}, 'PrintStream.println:')[0][1]
    if len(table) != 2 or {kind for _, _, _, kind in table} != {'RuntimeException', 'Error'} or len({handler for _, _, handler, _ in table}) != 1 or not all(int(a) <= at < int(b) for a, b, _, _ in table):
        raise ValueError('fixed diagnostic Runtime/Error cannot unwind either holding frame')
    loops = analyze(right); structural = no_branches(right)
    if structural['methodCount'] != 4 or 'BRANCH' in proof['allActualCounters'][KEY]:
        raise ValueError('actual four-method class has no conditional/switch and no raw branch counter')
    cases = json.loads(private.with_name('cases.safe.json').read_bytes())
    required = {('dev.codex.schubert.nk.web.bootstrap.'+c, m) for c, m in (
        ('WebRuntimeExecutionRetentionTest', 'exec325001UnknownCloseAndDiagnosticFailuresNeverUnwindOrRetry'),
        ('WebRuntimePendingFailureRetentionTest', 'exec325002PendingStartOrAwaitFailureKeepsTheExceptionalFinallyFrame'))}
    refs = [r for r in cases if (r['className'], r['method']) in required]
    if len(refs) != 2 or any(r['source'] != source or r['result'] != 'PASS_ORIGINAL_XML' for r in refs):
        raise ValueError('normal and exceptional finally independently observed in this exact source/run')
    branch = dict(structural, source=source, classSha256=current[KEY], rawCounterPreserved=True,
        branchCounter='NOT_APPLICABLE_NO_CONDITIONAL_OR_SWITCH')
    value = dict(actualExit=0, source=source, qualificationSha256=sha(qp), ownershipReviewed=True,
        changedPhysical=[KEY], unchangedPhysical=1666, finallyLoops=loops, preparedPrivateFinalPolicies=True,
        fixedDiagnosticProtected=True, classInitializationBeforeExecuteCallbacks=True, descriptorsPreserved=True,
        rawCounter=proof['allActualCounters'][KEY], branchlessOwnerProofs={KEY: branch}, actualExceptionCaseRefs=refs,
        branchPercentage=None, testsExecuted=0, additionalBuildsIssued=0, productionClassesExecuted=0, vmActions=0,
        formalAccepted=False, ptAlternativeCompleted=0, residual=['actualVM/Root/native/CHR/global100/F03/451 still separate',
            'arbitrary stop callback failure and VM fatal termination are outside this local proof'])
    os.umask(0o077); out = BASE/'PG6402-web-frame-order-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, finallyLoops=2, fences=10,
        branchApplicable=False, branchPercentage=None, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
