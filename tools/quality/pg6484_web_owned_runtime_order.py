"""Actual SSC327 Main bytes/default bindings/owner lock; does not load Production classes."""
import hashlib
import json
import os
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6056_expiry_read_methods import methods
from pg6084_web_factory_order import instructions
from pg6116_http_owner_order import resolved_body
from classfile_field_flags import fields
from pg6470_web_owned_component_selected import MAIN

CLS = 'dev.codex.schubert.nk.web.bootstrap.WebNativeRuntime'
JAR = 'src/schubert-nk-web/target/schubert-nk-web-0.1.0-SNAPSHOT.jar'
FLAGS = ('replies', 'replay', 'retry', 'http', 'management')


def analyze(raw, verbose, physical):
    flags = fields(physical)
    if any(flags[name.encode()]['flags'] != 0x0042 for name in FLAGS) or flags[b'ownerLock']['flags'] != 0x0012:
        raise ValueError('five private volatile handles and private final ownerLock required')
    blocks = methods(raw)
    starts = [v for k, v in blocks.items() if ' void start()' in k]
    closes = [v for k, v in blocks.items() if ' void close()' in k]
    if len(starts) != 1 or len(closes) != 1:
        raise ValueError('one start and close')
    for body in (starts[0], closes[0]):
        ops = instructions(body)
        monitors = [i for i, (_, op, _) in enumerate(ops) if op == 'monitorenter']
        if len(monitors) != 1 or not any(op == 'getfield' and 'ownerLock:' in arg for _, op, arg in ops[:monitors[0]]) or 'any' not in body:
            raise ValueError('same private ownerLock protects every exit of start/close')
    ops = instructions(starts[0])
    if any('close:' in arg for _, op, arg in ops if op.startswith('invoke')):
        raise ValueError('start cannot prematurely close a borrowed alias')
    acquired = (
        ('WebBrokerContexts.createRetainingUnknown:', 'broker:'),
        ('WebNativeCodecs.create:', 'codecs:'),
        ('ArtemisReplyConsumers.bind:', 'replies:'),
        ('WebLogReplayWorker.start:', 'replay:'),
        ('RevocationRetryWorker.start:', 'retry:'),
        ('WebManagementServer.bind:', 'management:'))
    captures = []
    for token, field in acquired:
        positions = [i for i, (_, op, arg) in enumerate(ops) if op.startswith('invoke') and token in arg]
        if len(positions) != 1 or ops[positions[0]+1][1] != 'putfield' or field not in ops[positions[0]+1][2]:
            raise ValueError('immediate acquired owner capture '+field)
        captures.append(dict(field=field[:-1], offset=ops[positions[0]+1][0]))
    directory = [i for i, (_, op, arg) in enumerate(ops) if op.startswith('invoke') and 'OwnedTransferDirectory.open:' in arg]
    if len(directory) != 2 or any(ops[i+1][1] != 'putfield' or field not in ops[i+1][2] for i, field in zip(directory, ('transfer:', 'assets:'))):
        raise ValueError('both directory roots captured before verification/borrowed use')
    offsets = [r['offset'] for r in captures]
    if offsets != sorted(offsets) or not offsets[1] < ops[directory[0]+1][0] < ops[directory[1]+1][0] < offsets[2]:
        raise ValueError('existing broker/codecs/two directories/replies/replay/retry/management acquisition order')
    default = [v for k, v in blocks.items() if k.startswith('  '+CLS+'(') and k.endswith('BooleanSupplier) throws java.io.IOException;')]
    if len(default) != 1 or sum(op == 'invokedynamic' for _, op, _ in instructions(default[0])) != 4:
        raise ValueError('one five-argument default delegates exactly four prepared method references')
    bootstraps = verbose.split('BootstrapMethods:', 1)[1]
    for binding in ('LinuxDirectoryCalls.create:', 'WebNativeRuntime.nativePath:', 'WebNativeRuntime.nativePort:', 'WebNativeRuntime.nativeVerify:'):
        if 'REF_invokeStatic dev/codex/schubert/nk/'+('storage/' if binding.startswith('Linux') else 'web/bootstrap/')+binding not in bootstraps:
            raise ValueError('fixed Production method reference '+binding)
    for signature, body in blocks.items():
        if ' boolean healthy()' in signature or ' boolean ready()' in signature:
            if any(op in ('putfield', 'putstatic', 'monitorenter') for _, op, _ in instructions(body)):
                raise ValueError('published state reads must not mutate/close/lock the runtime')
    return dict(fiveVolatileFlagsPreserved=True, privateFinalOwnerLock=True,
        startAndCloseSamePrivateMonitor=True, immediateCaptures=captures,
        directoryCaptureOffsets=[ops[i+1][0] for i in directory],
        fixedDefaultFourBindings=True, startClosesBorrowedAlias=False)


def main():
    qp = BASE/'PG6500-web-owned-component-qualification-v5/manifest.json'
    q = json.loads(qp.read_bytes()); pp = W/'pg6500-web-owned-component-qualification-v5/manifest.safe.json'
    if q['actualExit'] != 0 or (q['tests'], q['suites'], q['physicalMain']) != (27, 11, 1667) or sha(pp) != q['privateManifestSha256']:
        raise ValueError('genuine original27 all-source qualification first')
    proof = json.loads(pp.read_bytes()); source = q['source']
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    snapshot = W/'pg6498-web-owned-component-v5/source'; jar = snapshot/JAR
    prior = W/'pg6466-nio-collision-selected-v1/source'/JAR
    with zipfile.ZipFile(jar) as archive:
        physical = archive.read(CLS.replace('.', '/')+'.class')
        if {'web:'+n: hashlib.sha256(archive.read(n)).hexdigest() for n in archive.namelist() if n.endswith('.class')} != {k: v for k, v in proof['allPhysicalMainSha256'].items() if k.startswith('web:')}:
            raise ValueError('every original Web class/Jar byte matches the all-Main receipt')
    def read(path, verbose=False):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-v' if verbose else '-c', '-s', '-classpath', str(path), CLS], text=True)
    raw = read(jar); before, after = methods(read(prior)), methods(raw)
    old_verbose, current_verbose = read(prior, True), read(jar, True)
    preserved = [k for k in before if not k.startswith('  '+CLS+'(') and ' void start()' not in k]
    if any(k not in after or resolved_body(before[k], old_verbose) != resolved_body(after[k], current_verbose) for k in preserved):
        raise ValueError('all prior non-constructor/start methods including close lambdas retain exact normalized instructions and exception edges')
    owners = [p for p in ROOT.glob('src/*/src/main/java/**/*.java') if 'new WebNativeRuntime(' in p.read_text()]
    if len(owners) != 1 or not str(owners[0]).endswith('/WebProcessMain.java'):
        raise ValueError('sole Production construction remains WebProcessMain')
    caller = owners[0].read_text()
    if 'new WebNativeRuntime( pool, credentials, inputs.config(), ready, lifetime::stopping)' not in ' '.join(caller.split()):
        raise ValueError('Production has no configurable alternate IO ports')
    cases = json.loads(pp.with_name('cases.safe.json').read_bytes())
    refs = [r for r in cases if r['className'] == CLS+'OwnedComponentTest']
    if len(refs) != 7 or any(r['result'] != 'PASS_ORIGINAL_XML' for r in refs):
        raise ValueError('seven current original independent component cases only')
    value = dict(actualExit=0, source=source, qualificationSha256=sha(qp), classSha256=hashlib.sha256(physical).hexdigest(),
        sourceSha256=sha(snapshot/MAIN), structure=analyze(raw, current_verbose, physical),
        bootstrapHandlesAndAllArgumentsResolved=True,
        unchangedPriorMethods=len(preserved), soleProductionDefaultCaller=True, actualCaseRefs=refs,
        publicAlternativeConfigAdded=False, startupOrderChanged=False, ownComponentOnly=True,
        nativeRootOrAuthorizationProven=False, productionTestsExecutedByReader=0, buildsIssued=0,
        vmActions=0, ptAlternativeCompleted=0, formalAccepted=False, effortPercent=None)
    out = BASE/'PG6484-web-owned-runtime-order-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
