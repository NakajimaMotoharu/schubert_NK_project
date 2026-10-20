"""Actual original JVM ownership/exception ranges and public ABI; no Production invocation."""
import hashlib
import json
import os
import re
import subprocess
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6082_web_factory_qualification import SOURCE
from pg6056_expiry_read_methods import methods
from pg6078_jms_owner_order import factory_last, group_capacity
from pg6072_jms_owner_initial_gap import OWNERS

CLASS = 'dev.codex.schubert.nk.web.messaging.WebBrokerContexts'


def instructions(code):
    return [(int(n), op, arg) for n, op, arg in re.findall(r'(?m)^\s*(\d+):\s+(\w+)([^\n]*)', code)]


def narrow_or_wide_literal_body(code):
    """Retain every literal/member/branch target and exception edge,normalize only ldc width."""
    ops = instructions(code); offsets = {at: i for i, (at, _, _) in enumerate(ops)}
    result = []
    for _, op, arg in ops:
        if op == 'goto' or op.startswith('if'):
            arg = 'targetInstruction='+str(offsets[int(arg.strip())])
        result.append(('ldc' if op == 'ldc_w' else op, re.sub(r'\s+', ' ', arg).strip()))
    edges = [(offsets[int(a)], offsets[int(b)], offsets[int(c)], kind.strip())
             for a, b, c, kind in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+(Class [^\n]+|any)\s*$', code)]
    return result, edges


def context_bootstrap(code, verbose):
    found = re.findall(r'// InvokeDynamic #(\d+):open:', code)
    if len(found) != 1:
        raise ValueError('one contexts open lambda callsite')
    section = verbose.split('BootstrapMethods:', 1)[1]
    match = re.search(r'(?m)^  '+found[0]+r':[^\n]*\n(?:(?!  \d+:|InnerClasses:)[^\n]*\n)*', section)
    if not match:
        raise ValueError('actual bootstrap method and all arguments')
    normalized = re.sub(r'#\d+', '#CP', match.group(0))
    normalized = re.sub(r'^  \d+:', '  index:', normalized)
    if 'REF_invokeVirtual '+CLASS.replace('.', '/')+'.open:()Ljakarta/jms/JMSContext;' not in normalized:
        raise ValueError('contexts lambda still targets exact private open method')
    return re.sub(r'InvokeDynamic #\d+:', 'InvokeDynamic #resolved:', code), normalized


def factory_owner(blocks):
    constructors = [v for k, v in blocks.items() if k.startswith('  private '+CLASS+'(')]
    if len(constructors) != 1:
        raise ValueError('one prepared private owner constructor')
    code = constructors[0]; ops = instructions(code)
    calls = [i for i, (_, op, arg) in enumerate(ops) if op == 'invokestatic' and 'Method newFactory:' in arg]
    if len(calls) != 1:
        raise ValueError('one factory acquisition inside prepared owner')
    before, after = ops[:calls[0]], ops[calls[0]+1:]
    for field in ('stateLock:', 'passwords:'):
        if sum(op == 'putfield' and '// Field '+field in arg for _, op, arg in before) != 1:
            raise ValueError('lock/password port completed before resource acquisition')
    if [op for _, op, _ in after] != ['astore_3', 'aload_0', 'aload_3', 'putfield', 'aload_0', 'aload_3', 'putfield', 'return']:
        raise ValueError('after configured factory only two final same-reference stores and return')
    if ['factory:Ljakarta/jms/ConnectionFactory;', 'owner:Ljava/lang/AutoCloseable;'] != [arg.split('// Field ', 1)[1].strip() for _, op, arg in after if op == 'putfield']:
        raise ValueError('factory ownership retained in exact fields')
    helper = [v for k, v in blocks.items() if ' configureOwned(' in k]
    if len(helper) != 1:
        raise ValueError('one factory configuration ownership helper')
    helper = helper[0]; h = instructions(helper)
    acquired = [at for at, op, arg in h if op == 'invokeinterface' and 'java/util/function/Supplier.get:' in arg]
    setters = [(at, arg.split('ActiveMQConnectionFactory.', 1)[1].split(':', 1)[0]) for at, op, arg in h
               if op == 'invokevirtual' and 'ActiveMQConnectionFactory.set' in arg]
    names = ['setCallTimeout', 'setClientFailureCheckPeriod', 'setConnectionTTL', 'setInitialConnectAttempts',
             'setReconnectAttempts', 'setRetryInterval', 'setRetryIntervalMultiplier', 'setMaxRetryInterval',
             'setConsumerWindowSize', 'setBlockOnDurableSend', 'setPreAcknowledge', 'setUseTopologyForLoadBalancing']
    closed = [at for at, op, arg in h if op == 'invokevirtual' and 'ActiveMQConnectionFactory.close:' in arg]
    ranges = [(int(a), int(b), int(c), kind) for a, b, c, kind in re.findall(
        r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class (java/lang/(?:RuntimeException|Error))\s*$', helper)]
    if len(acquired) != 1 or [name for _, name in setters] != names or len(closed) != 1 or len(ranges) != 4:
        raise ValueError('exact single acquire/twelve settings/one close/two typed handler pairs')
    for kind in ('java/lang/RuntimeException', 'java/lang/Error'):
        for at, _ in setters:
            if not any(a <= at < b and k == kind for a, b, _, k in ranges):
                raise ValueError('every setting protected against RuntimeException and Error')
        if not any(a <= closed[0] < b and k == kind for a, b, _, k in ranges):
            raise ValueError('single close has independent typed failure protection')
    if not acquired[0] < min(a for a, _, _, _ in ranges):
        raise ValueError('getter failure is not treated as owned resource configuration failure')
    return dict(constructorCodeSha256=hashlib.sha256(code.encode()).hexdigest(),
                configurationCodeSha256=hashlib.sha256(helper.encode()).hexdigest(),
                acquisitionOffset=acquired[0], setterOffsets=[at for at, _ in setters], closeOffset=closed[0],
                exceptionRanges=ranges, finalSameReferenceStoresOnly=True, configurationAndCloseProtected=True)


def main():
    qpath = BASE/'PG6082-web-factory-qualification-v1/manifest.json'; q = json.loads(qpath.read_bytes())
    private = W/'pg6082-web-factory-qualification-v1/manifest.safe.json'
    if (q['source'] != SOURCE or q['actualExit'] != 0 or (q['tests'], q['suites'], q['physicalMain']) != (925, 150, 1667)
            or q['privateManifestSha256'] != sha(private)):
        raise ValueError('genuine current925 original artifact qualification first')
    proof = json.loads(private.read_bytes()); oldbase = W/'pg6074-jms-owner-selected-v1/source/src'
    currentbase = W/'pg6086-web-factory-selected-v2/source/src'
    def text(module, cls, old=False, public=False):
        jar = (oldbase if old else currentbase)/('schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), *(['-public', '-s'] if public else ['-p', '-c', '-s']),
                                        '-classpath', str(jar), cls], text=True)
    current, prior = methods(text('web', CLASS)), methods(text('web', CLASS, old=True))
    own = factory_owner(current)
    changed = {k for k in prior if current.get(k) != prior[k]}
    wanted = {k for k in prior if ' create(' in k or ' newFactory(' in k}
    close_key = '  public void close();'
    context_key = '  public '+CLASS.rsplit('.', 1)[0]+'.JmsContextFactory contexts();'
    if narrow_or_wide_literal_body(current[close_key]) != narrow_or_wide_literal_body(prior[close_key]):
        raise ValueError('existing close instructions/literals/branches/exception edges unchanged except ldc width')
    def verbose(old):
        jar = (oldbase if old else currentbase)/'schubert-nk-web/target/schubert-nk-web-0.1.0-SNAPSHOT.jar'
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-v', '-classpath', str(jar), CLASS], text=True)
    if context_bootstrap(current[context_key], verbose(False)) != context_bootstrap(prior[context_key], verbose(True)):
        raise ValueError('contexts instruction/callsite/resolved bootstrap arguments unchanged')
    representation_only = changed & {close_key, context_key}
    changed -= representation_only
    added = set(current)-set(prior)
    if changed != wanted or set(prior)-set(current) or len(added) != 3 or not all(
            ' configureOwned(' in k or ' lambda$newFactory$' in k or k.startswith('  private '+CLASS+'(') for k in added):
        raise ValueError('only create/newFactory and three declared private/helper bodies change;live open/close unchanged')
    if text('web', CLASS, public=True) != text('web', CLASS, old=True, public=True):
        raise ValueError('public ABI unchanged')
    consumers = [factory_last(methods(text(module, cls)), cls, factory) for module, cls, factory in OWNERS]
    api = 'dev.codex.schubert.nk.api.messaging.inbound.ApiMessagingRuntime'
    group = [v for v in methods(text('api', api)).values() if 'SyncRequestConsumers.start:' in v]
    if len(group) != 1:
        raise ValueError('one parent fixed-capacity group capture')
    capacity = group_capacity(group[0])
    sync = 'dev.codex.schubert.nk.api.messaging.inbound.SyncRequestConsumers'
    if methods(text('api', sync)) != methods(text('api', sync, old=True)):
        raise ValueError('Sync preallocated four-context owner implementation unchanged')
    sc = [v for v in methods(text('api', sync)).values() if 'java/util/List.add:' in v]
    if len(sc) != 1 or not re.search(r'iconst_4[\s\S]{0,150}java/util/ArrayList\."<init>":\(I\)V', sc[0]):
        raise ValueError('four-context backing storage prepared once')
    if not sc[0].index('java/util/ArrayList."<init>":(I)V') < sc[0].index('Method "<init>":(Ljava/util/List;)V') < sc[0].index('java/util/function/Supplier.get:') < sc[0].index('java/util/List.add:'):
        raise ValueError('Sync owner and bounded capture storage precede acquisition/setup')
    if sc[0].count('java/util/List.add:') != 1 or sc[0].count('java/util/function/Supplier.get:') != 1 or 'if_icmpge' not in sc[0]:
        raise ValueError('one bounded context acquisition/capture site')
    result = dict(actualExit=0, source=SOURCE, qualificationSha256=sha(qpath),
        providerOwnership=own, consumerOwners=consumers, groupCapture=capacity,
        syncFourCaptureCodeSha256=hashlib.sha256(sc[0].encode()).hexdigest(),
        publicAbiUnchanged=True, existingOpenCloseAndInjectedConstructorUnchanged=True,
        changedMethods=sorted(changed), addedMethods=sorted(added),
        representationOnlyMethods=sorted(representation_only),
        allOwnershipBoundariesVerified=True, testsExecuted=0, additionalBuildsIssued=0,
        dynamicOomExecuted=False, actualRuntimeProven=False, currentWholePending=True,
        formalAccepted=False, ptAlternativeCompleted=0, physicalMain=proof['physicalMain'])
    os.umask(0o077); out = BASE/'PG6084-web-factory-order-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, manifestSha256=sha(out/'manifest.json'),
                         publicAbiUnchanged=True, allOwnershipBoundariesVerified=True)))


if __name__ == '__main__':
    main()
