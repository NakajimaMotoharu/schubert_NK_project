"""Current original JVM close/ownership/configuration/ABI, no production execution."""
import json
import os
import re
import subprocess
import sys
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6056_expiry_read_methods import methods
from pg6084_web_factory_order import instructions
from pg6116_http_owner_order import resolved_body
from pg6148_api_jms_close_order import close_proofs
from pg6078_jms_owner_order import group_capacity
from pg6156_api_factory_close_qualification_v2 import SOURCE

PROVIDER = 'dev.codex.schubert.nk.api.messaging.config.ArtemisConnectionFactoryProvider'
BROKER = 'dev.codex.schubert.nk.api.messaging.config.ApiBrokerContexts'


def configuration(blocks):
    helpers = [v for k, v in blocks.items() if ' configureOwned(' in k]
    if len(helpers) != 1: raise ValueError('one exact API configuration helper')
    code = helpers[0]; ops = instructions(code)
    acquire = [at for at, op, arg in ops if op == 'invokeinterface' and 'java/util/function/Supplier.get:' in arg]
    setters = [(at, arg.split('ActiveMQConnectionFactory.',1)[1].split(':',1)[0]) for at, op, arg in ops if op == 'invokevirtual' and 'ActiveMQConnectionFactory.set' in arg]
    names = ['setCallTimeout','setClientFailureCheckPeriod','setConnectionTTL','setInitialConnectAttempts',
        'setReconnectAttempts','setRetryInterval','setRetryIntervalMultiplier','setMaxRetryInterval',
        'setConsumerWindowSize','setBlockOnDurableSend','setPreAcknowledge','setUseTopologyForLoadBalancing']
    close = [at for at, op, arg in ops if op == 'invokevirtual' and 'ActiveMQConnectionFactory.close:' in arg]
    ranges = [(int(a),int(b),int(c),kind) for a,b,c,kind in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class (java/lang/(?:RuntimeException|Error))\s*$', code)]
    if len(acquire)!=1 or [name for _,name in setters]!=names or len(close)!=1 or len(ranges)!=4:
        raise ValueError('exact acquire/twelve setters/one close/two typed handler pairs')
    for kind in ('java/lang/RuntimeException','java/lang/Error'):
        for at in [*(at for at,_ in setters),close[0]]:
            if not any(a<=at<b and k==kind for a,b,_,k in ranges):
                raise ValueError('each setter and close independently protected against both types')
    if not acquire[0]<min(a for a,_,_,_ in ranges):
        raise ValueError('factory acquisition not mistaken for an already owned resource')
    return dict(acquireOffset=acquire[0],setterOffsets=[at for at,_ in setters],closeOffset=close[0],typedRanges=ranges)


def broker_preparation(blocks):
    constructors = [v for k,v in blocks.items() if k.startswith('  private '+BROKER+'(') and 'java/util/function/BiFunction.apply:' in v]
    if len(constructors)!=1: raise ValueError('one provider-taking constructor')
    ops=instructions(constructors[0]); calls=[i for i,(_,op,arg) in enumerate(ops) if op=='invokeinterface' and 'BiFunction.apply:' in arg]
    if len(calls)!=3: raise ValueError('exact three fixed provider acquire sites')
    for field in ('stateLock','passwords','owners','ownerClosed'):
        if sum(op=='putfield' and '// Field '+field+':' in arg for _,op,arg in ops[:calls[0]])!=1:
            raise ValueError('all broker state/ports/phases before first acquisition')
    allocations=[i for i,(_,op,_) in enumerate(ops) if op in ('new','anewarray','newarray','multianewarray')]
    if not allocations or max(allocations)>=calls[0]: raise ValueError('no post-acquire owner/state allocation')
    code=constructors[0]
    if not re.search(r'iconst_3[\s\S]{0,150}java/util/ArrayList\."<init>":\(I\)V',code) or not re.search(r'iconst_3[^\n]*\n[^\n]*newarray\s+boolean',code):
        raise ValueError('both owner capacity and phase slots exactly3')
    if sum(op=='invokeinterface' and 'java/util/List.add:' in arg for _,op,arg in ops)!=3:
        raise ValueError('three stores into the already allocated owner capacity')
    for field in ('retainedSync','retainedWebLog','retainedAsync'):
        positions=[i for i,(_,op,arg) in enumerate(ops) if op=='putfield' and '// Field '+field+':' in arg]
        if len(positions)!=1 or positions[0]<=calls[-1]: raise ValueError('final factory fields after all successful acquisitions')
    return dict(acquireInstructionIndices=calls,allStatePreparedBeforeFirst=True,preallocatedCapacity=3,postAcquireAllocations=0)


def main(expected_sha):
    if not re.fullmatch('[0-9a-f]{64}',expected_sha): raise ValueError('exact independent qualification SHA')
    qp=BASE/'PG6156-api-factory-close-qualification-v2/manifest.json'
    if sha(qp)!=expected_sha: raise ValueError('immutable original1955 qualification')
    q=json.loads(qp.read_bytes())
    if q['actualExit']!=0 or q['source']!=SOURCE or (q['tests'],q['suites'],q['physicalMain'])!=(1955,321,1667):
        raise ValueError('genuine source/run and complete original XML/physical first')
    jars=[W/(run+'/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar') for run in ('pg6130-api-management-stop-green-v1','pg6154-api-factory-close-selected-v2')]
    def read(cls,old=False,flags=('-p','-c','-s')):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),*flags,'-classpath',str(jars[0 if old else 1]),cls],text=True)
    close=close_proofs(jars); provider=methods(read(PROVIDER)); broker=methods(read(BROKER))
    if read(PROVIDER,flags=('-public','-s'))!=read(PROVIDER,old=True,flags=('-public','-s')):
        raise ValueError('provider public ABI unchanged')
    conf=configuration(provider); prep=broker_preparation(broker)
    runtime='dev.codex.schubert.nk.api.messaging.inbound.ApiMessagingRuntime'
    groups=[v for v in methods(read(runtime)).values() if 'SyncRequestConsumers.start:' in v]
    if len(groups)!=1: raise ValueError('one bounded group collector')
    capacity=group_capacity(groups[0])
    group_ops=instructions(groups[0])
    init=[at for at,op,arg in group_ops if op=='invokespecial' and ('// Method "<init>":' in arg or '// Method '+runtime.replace('.','/')+'."<init>":' in arg)]
    child=[at for at,_,arg in group_ops if 'SyncRequestConsumers.start:' in arg]
    if len(init)!=1 or len(child)!=1 or init[0]>=child[0]:
        raise ValueError('prepared parent owner must precede child acquisition')
    nested=[k for k in q['changedPhysical'] if '$' in k]
    for item in nested:
        module,member=item.split(':',1)
        if module!='api': raise ValueError('only declared API nested/debug changes')
        cls=member[:-6].replace('/','.')
        before,after=methods(read(cls,old=True)),methods(read(cls))
        if set(before)!=set(after): raise ValueError('nested executable ABI unchanged')
        verbose_old,verbose_new=read(cls,old=True,flags=('-p','-v')),read(cls,flags=('-p','-v'))
        if any(resolved_body(before[k],verbose_old)!=resolved_body(after[k],verbose_new) for k in before):
            raise ValueError('nested differences debug-only; actual bootstrap bindings checked')
    value=dict(actualExit=0,source=SOURCE,qualificationSha256=expected_sha,closeOwners=close,
        providerConfiguration=conf,brokerPreparation=prep,groupCapacity=capacity,nestedDebugOnly=nested,
        publicAbiUnchanged=True,testsExecuted=0,buildsIssued=0,nativeRetentionPending=True,
        fullCurrentWholePending=True,formalAccepted=False,nativeQualified=False,ptAlternativeCompleted=0)
    os.umask(0o077);out=BASE/'PG6158-api-factory-close-order-v2';out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=SOURCE,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__': main(sys.argv[1])
