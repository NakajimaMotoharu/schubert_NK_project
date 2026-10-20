"""Actual candidate Jar ownership order and ABI; never invokes Production or induces heap failure."""
import hashlib
import json
import os
import re
import subprocess
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6076_jms_owner_qualification import SOURCE
from pg6072_jms_owner_initial_gap import OWNERS
from pg6056_expiry_read_methods import methods

QUALIFICATION_SHA = '4524bb06ba03d4dae2e9f3c5d280bf7fa648967277f7bb07de38142f9f2748c9'


def factory_last(blocks, cls, factory):
    constructors = [(k, v) for k, v in blocks.items() if k.startswith('  private '+cls+'(')]
    if len(constructors) != 1:
        raise ValueError('one private factory-taking owner constructor')
    name, code = constructors[0]
    instructions = [(int(n), op, args) for n, op, args in re.findall(r'(?m)^\s*(\d+):\s+(\w+)([^\n]*)', code)]
    acquires = [i for i, (_, op, arg) in enumerate(instructions) if op == 'invokeinterface' and factory in arg]
    if len(acquires) != 1 or any(factory in v for k, v in blocks.items() if k != name):
        raise ValueError('the single factory acquisition occurs inside fully prepared owner,not in caller')
    index = acquires[0]; before, after = instructions[:index], instructions[index+1:]
    if not any(op == 'new' for _, op, _ in before) or any(op.startswith(('new', 'anewarray', 'multianewarray')) for _, op, _ in after):
        raise ValueError('all coded state/array allocations precede resource acquisition')
    for _, op, arg in after:
        if re.fullmatch(r'(aload|astore)(?:_\d)?', op) or op in ('ldc', 'checkcast', 'return'):
            continue
        if op == 'invokestatic' and 'java/util/Objects.requireNonNull:' in arg:
            continue
        if op == 'putfield' and '// Field context:Ljakarta/jms/JMSContext;' in arg:
            continue
        raise ValueError('only fixed nonnull check/cast/final context storage/return after acquire,no unknown call or callback')
    if sum(op == 'putfield' and '// Field context:Ljakarta/jms/JMSContext;' in arg for _, op, arg in after) != 1 or not after or after[-1][1] != 'return':
        raise ValueError('final nonnull ownership established once before constructor completes')
    return dict(className=cls, constructor=name, factoryInstructionOffset=instructions[index][0],
        statePreparedBeforeFactory=True, postAcquireOpcodes=[op for _, op, _ in after],
        constructorCodeSha256=hashlib.sha256(code.encode()).hexdigest())


def group_capacity(code):
    if (not re.search(r'iconst_3[\s\S]{0,150}invokespecial[^\n]*java/util/ArrayList\."<init>":\(I\)V', code)
            or code.count('Method java/util/ArrayList.add:') != 3
            or code.index('java/util/ArrayList."<init>":(I)V') >= code.index('SyncRequestConsumers.start:')):
        raise ValueError('capacity3 before any acquisition,three bounded group add sites')
    for at, target in re.findall(r'(?m)^\s*(\d+):\s+goto\s+(\d+)', code):
        if int(target) <= int(at):
            raise ValueError('no backward group-collection loop may exceed fixed capacity')
    return dict(maximumGroups=3, addSites=3, capacityPreparedBeforeAcquisition=True,
        codeSha256=hashlib.sha256(code.encode()).hexdigest())


def main():
    qpath = BASE/'PG6076-jms-owner-qualification-v1/manifest.json'
    if sha(qpath) != QUALIFICATION_SHA:
        raise ValueError('genuine1933/static/physical qualification first;placeholder is fail-closed')
    q = json.loads(qpath.read_bytes())
    if q['source'] != SOURCE or (q['tests'], q['suites'], q['physicalMain']) != (1933, 317, 1667):
        raise ValueError('one exact candidate source/run')
    base = W/'pg6074-jms-owner-selected-v1/source/src'
    oldbase = W/'pg6066-original3979-artifacts-v1/jars'
    def text(module, cls, old=False, flags=('-p', '-c', '-s')):
        jar = oldbase/('schubert-nk-'+module+'.jar') if old else base/('schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), *flags, '-classpath', str(jar), cls], text=True)
    facts, abi = [], {}
    for module, cls, factory in OWNERS:
        facts.append(factory_last(methods(text(module, cls)), cls, factory))
        current = text(module, cls, flags=('-public', '-s'))
        if current != text(module, cls, old=True, flags=('-public', '-s')):
            raise ValueError('all existing public consumer signatures unchanged')
        abi[cls] = hashlib.sha256(current.encode()).hexdigest()
    cls = 'dev.codex.schubert.nk.api.messaging.inbound.ApiMessagingRuntime'
    code = [v for v in methods(text('api', cls)).values() if 'SyncRequestConsumers.start:' in v]
    if len(code) != 1 or text('api', cls, flags=('-public', '-s')) != text('api', cls, old=True, flags=('-public', '-s')):
        raise ValueError('one group collector/public assembly ABI unchanged')
    groups = group_capacity(code[0]); nested = [k for k in q['changedPhysical'] if '$' in k]
    for key in nested:
        module, member = key.split(':', 1); name = member[:-6].replace('/', '.')
        if methods(text(module, name)) != methods(text(module, name, old=True)):
            raise ValueError('declared nested difference must be debug-only,not extra executable change')
    result = dict(actualExit=0, source=SOURCE, qualificationSha256=sha(qpath), consumerOwners=facts,
        groupCapture=groups, publicAbiUnchanged=True, publicAbiSha256=abi, nestedDebugOnly=nested,
        codeGapCorrections=4, dynamicOomExecuted=False, productionMethodsInvoked=0, testsExecuted=0,
        additionalBuildsIssued=0, formalAccepted=False, ykt1297ProviderFactoryCandidatePending=True)
    os.umask(0o077); out = BASE/'PG6078-jms-owner-order-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, corrected=4, nested=nested, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
