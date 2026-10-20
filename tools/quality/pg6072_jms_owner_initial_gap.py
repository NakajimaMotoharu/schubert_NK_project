"""Actual archived Jar control-flow facts for BUG1537; no Production invocation or heap exhaustion."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6054_expiry_read_qualification import SOURCE
from pg6056_expiry_read_methods import methods

OWNERS = (
    ('api', 'dev.codex.schubert.nk.api.messaging.inbound.QuestionWorkConsumers', 'java/util/function/Supplier.get:'),
    ('api', 'dev.codex.schubert.nk.api.messaging.inbound.WebLogConsumers', 'java/util/function/Supplier.get:'),
    ('web', 'dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumers', 'dev/codex/schubert/nk/web/messaging/JmsContextFactory.open:'))


def unprotected_constructor_gap(blocks, cls, factory):
    key = '  private '+cls+'(jakarta.jms.JMSContext);'
    ctor = blocks[key]
    candidates = [(k, v) for k, v in blocks.items() if factory in v]
    if len(candidates) != 1:
        raise ValueError('one explicit caller acquisition method')
    caller, code = candidates[0]
    calls = list(re.finditer(r'(?m)^\s*(\d+):\s+invokeinterface[^\n]*'+re.escape(factory), code))
    enters = list(re.finditer(r'(?m)^\s*(\d+):\s+invokespecial[^\n]*"<init>":\(Ljakarta/jms/JMSContext;\)V', code))
    if len(calls) != 1 or len(enters) != 1 or int(calls[0][1]) >= int(enters[0][1]):
        raise ValueError('actual acquisition precedes this exact consumer constructor invocation')
    ranges = [(int(a), int(b)) for a, b in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+\d+\s+(?:Class|any)', code)]
    if any(a <= int(enters[0][1]) < b for a, b in ranges):
        raise ValueError('constructor is already protected,not this unprotected gap')
    allocations = re.findall(r'(?m)^\s*\d+:\s+new\s+[^\n]*// class (java/util/concurrent/(?:atomic/AtomicBoolean|locks/ReentrantLock))', ctor)
    if not allocations or 'putfield' not in ctor or '// Field context:Ljakarta/jms/JMSContext;' not in ctor:
        raise ValueError('actual state allocations occur inside constructor before context ownership assignment')
    return dict(className=cls, caller=caller, factoryInstructionOffset=int(calls[0][1]), constructorInstructionOffset=int(enters[0][1]),
        constructorOutsideAllExceptionRanges=True, fieldAllocations=allocations,
        constructorCodeSha256=hashlib.sha256(ctor.encode()).hexdigest(), callerCodeSha256=hashlib.sha256(code.encode()).hexdigest())


def main():
    p = W/'pg6054-expiry-read-qualification-v1/manifest.safe.json'
    if sha(p) != '14128e3496c796aca15bb9bd8bc46d87a2662a34e8f412125d1b667ff029c885':
        raise ValueError('actual sourcec4 original148 Main Jar/8511667 proof')
    qualified = json.loads(p.read_bytes()); jars = {}
    for module in ('api', 'web'):
        jar = W/('pg6052-expiry-combined-green-v1/source/src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        with zipfile.ZipFile(jar) as z:
            actual = {module+':'+n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
        if actual != {k: v for k, v in qualified['allPhysicalMainSha256'].items() if k.startswith(module+':')}:
            raise ValueError('every original Main class byte retained,not rebuilt')
        jars[module] = jar
    def blocks(module, cls):
        text = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jars[module]), cls], text=True)
        return methods(text)
    facts = [unprotected_constructor_gap(blocks(module, cls), cls, factory) for module, cls, factory in OWNERS]
    groupcls = 'dev.codex.schubert.nk.api.messaging.inbound.ApiMessagingRuntime'
    group = [v for v in blocks('api', groupcls).values() if 'SyncRequestConsumers.start:' in v]
    if len(group) != 1 or 'Method java/util/ArrayList."<init>":()V' not in group[0] or group[0].index('SyncRequestConsumers.start:') >= group[0].index('Method java/util/ArrayList.add:'):
        raise ValueError('default empty group list grows only after first acquired group returns')
    value = dict(actualExit=0, source=SOURCE, sourceQualificationSha256=sha(p), owners=facts,
        additionalGroupCapture=dict(className=groupcls, defaultCapacityBeforeFirstAcquire=True, firstAddAfterFirstAcquiredGroup=True,
            codeSha256=hashlib.sha256(group[0].encode()).hexdigest()),
        staticCounterexamples=4, dynamicOomExecuted=False, productionMethodsInvoked=0, testsExecuted=0,
        additionalBuildsIssued=0, sourceCodeChanged=False, formalAccepted=False, ptAlternativeCompleted=0,
        originalJarSha256={k: sha(v) for k, v in jars.items()})
    os.umask(0o077); out = BASE/'PG6072-jms-owner-gap-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, staticCounterexamples=4, testsExecuted=0, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
