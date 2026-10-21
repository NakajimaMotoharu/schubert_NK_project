"""YKT1335 ordinary bounded collections only; actual whole refs required, no heap exhaustion."""
import hashlib
import json
import os
import subprocess
import zipfile
from pg5940_private_lock_compile import W, BASE, TC, sha as path_sha
from pg6056_expiry_read_methods import methods
from pg6084_web_factory_order import instructions
from pg6078_jms_owner_order import group_capacity
from pg6446_morning_sequence_capacity import analyze as morning_capacity
from pg6506_current4064_trace import SOURCE, read_qualified

OWNERS = {
    'api.messaging.inbound.ApiMessagingRuntime': ('api', 'ApiMessagingRuntimeTest'),
    'api.messaging.inbound.SyncRequestConsumers': ('api', 'SyncRequestConsumersTest'),
    'api.messaging.config.ApiBrokerContexts': ('api', 'ApiBrokerContextsTest'),
    'batch.file.MorningStartupLaunchOwner': ('batch', 'MorningStartupLaunchOwnerTest'),
}


def sync_capacity(code):
    ops = instructions(code)
    constructors = [i for i, (_, op, arg) in enumerate(ops) if op == 'invokespecial' and 'ArrayList."<init>":(I)V' in arg]
    acquires = [i for i, (_, op, arg) in enumerate(ops) if op.startswith('invoke') and 'Supplier.get:' in arg]
    adds = [i for i, (_, op, arg) in enumerate(ops) if op.startswith('invoke') and 'List.add:' in arg]
    bounds = [i for i, (_, op, _) in enumerate(ops) if op == 'if_icmpge' and i > 0 and ops[i-1][1] == 'iconst_4']
    if len(constructors) != 1 or ops[constructors[0]-1][1] != 'iconst_4' or len(acquires) != 1 or len(adds) != 1 or len(bounds) != 1 or not constructors[0] < bounds[0] < acquires[0] < adds[0]:
        raise ValueError('one capacity4 before fixed four-loop/context acquire and immediate registration')
    if any('JMSContext.' in arg for _, op, arg in ops[acquires[0]+1:adds[0]] if op.startswith('invoke')):
        raise ValueError('context registration before any provider use')
    return dict(capacity=4, maximumAdds=4, constructorOffset=ops[constructors[0]][0], acquireOffset=ops[acquires[0]][0], addOffset=ops[adds[0]][0])


def factory_capacity(code):
    ops = instructions(code)
    constructors = [i for i, (_, op, arg) in enumerate(ops) if op == 'invokespecial' and 'ArrayList."<init>":(I)V' in arg]
    acquires = [i for i, (_, op, arg) in enumerate(ops) if op.startswith('invoke') and 'BiFunction.apply:' in arg]
    adds = [i for i, (_, op, arg) in enumerate(ops) if op.startswith('invoke') and 'List.add:' in arg]
    if len(constructors) != 1 or ops[constructors[0]-1][1] != 'iconst_3' or len(acquires) != 3 or len(adds) != 3:
        raise ValueError('capacity3 and exactly three factory/add sites')
    sequence = [constructors[0], *[v for pair in zip(acquires, adds) for v in pair]]
    if sequence != sorted(sequence):
        raise ValueError('capacity before each acquisition followed by collection registration')
    return dict(capacity=3, maximumAdds=3, acquireOffsets=[ops[i][0] for i in acquires], addOffsets=[ops[i][0] for i in adds])


def compiled_shapes():
    snapshot = W/'pg6498-web-owned-component-v5/source'; result = []
    for cls, (module, test) in OWNERS.items():
        jar = snapshot/('src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        name = 'dev.codex.schubert.nk.'+cls
        raw = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jar), name], text=True)
        blocks = methods(raw)
        if cls.endswith('ApiMessagingRuntime'):
            bodies = [v for v in blocks.values() if 'SyncRequestConsumers.start:' in v]
            if len(bodies) != 1: raise ValueError('one bounded group collector')
            proof = group_capacity(bodies[0])
        elif cls.endswith('SyncRequestConsumers'):
            bodies = [v for v in blocks.values() if 'java/util/ArrayList."<init>"' in v]
            if len(bodies) != 1: raise ValueError('one bounded context collector')
            proof = sync_capacity(bodies[0])
        elif cls.endswith('ApiBrokerContexts'):
            bodies = [v for k, v in blocks.items() if k.startswith('  private '+name+'(') and 'java/util/ArrayList."<init>"' in v]
            if len(bodies) != 1: raise ValueError('one prepared three-factory constructor')
            proof = factory_capacity(bodies[0])
        else:
            proof = morning_capacity(blocks, True)
        with zipfile.ZipFile(jar) as archive:
            key = module+':'+name.replace('.', '/')+'.class'
            digest = hashlib.sha256(archive.read(name.replace('.', '/')+'.class')).hexdigest()
        result.append(dict(className=name, module=module, physicalKey=key, classSha256=digest, testClass=test, capacityProof=proof))
    return result


def main():
    qp, q = read_qualified(); cases = json.loads(qp.with_name('cases.json').read_bytes())
    result = compiled_shapes()
    for row in result:
        if q['allPhysicalMainSha256'][row['physicalKey']] != row['classSha256']:
            raise ValueError('current genuine whole Jar bytes, not older JVM evidence')
        suffix = row['className'].rsplit('.',1)[0]+'.'+row['testClass']
        refs = [r for r in cases if r['class'] == suffix]
        if not refs or any(r['source'] != SOURCE or r['result'] != 'PASS_ORIGINAL_XML' for r in refs):
            raise ValueError('actual current whole semantic Test class required for each ordinary target')
        row['currentWholeCaseRefs'] = [{k:r[k] for k in ('testId','class','caseNameSha256','xmlSha256','source')} for r in refs]
    value = dict(actualExit=0, source=SOURCE, currentWholeQualificationSha256=path_sha(qp),
        readerAttempt=2, priorReaderFailurePreserved='1410/BUG1588/original84694 exit1 before output creation',
        ordinaryTargets=result, productionCodeChanged=False, testsExecuted=0, buildsIssued=0,
        ordinaryFourCollectionFirstGrowRiskPresent=False, heapFailureInjected=False, broaderYktClosed=False,
        candidateSearchCompleted=False, broaderUnreviewedCandidatesRemain=True,
        heldRootOrRecoveryAssessed=False, nativeOwnershipProven=False, formalAccepted=False,
        ptAlternativeCompleted=0, effortPercent=None)
    out = BASE/'PG6510-owned-collection-capacity-v2'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, targets=len(result), broaderYktClosed=False, manifestSha256=path_sha(out/'manifest.json'))))


if __name__ == '__main__': main()
