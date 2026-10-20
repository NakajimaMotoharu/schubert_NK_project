"""Source/JVM review of SS319 plus unchanged management/keeper ownership; no new PT/VM."""
import re
import pg6234_web_keeper_order as previous
from pg6248_normal_phase_qualification import original_source


def rollback_review(read):
    p=previous.previous.profile.prior
    prefix='api.messaging.inbound.'
    table=p.methods(read('api',prefix+'InboundTransactions'))
    rollback=next(v for k,v in table.items() if 'rollbackAfterFailure('in k and 'Runnable'in k)
    calls=p.one_call({'rollback':rollback},'java/lang/Runnable.run:',2)
    action=p.one_call({'rollback':rollback},'jakarta/jms/JMSContext.rollback:')[0]
    validations=p.one_call({'rollback':rollback},'Objects.requireNonNull:',2)
    if not max(c[1]for c in validations)<calls[0][1]<action[1]<calls[1][1]:
        raise ValueError('both ports validated, attempt then actual rollback then confirmation')
    edges=previous.exception_edges(rollback)
    if len(edges)!=1 or edges[0][3]!='java/lang/RuntimeException' or not edges[0][0]<=action[1]<edges[0][1]:
        raise ValueError('only RuntimeException around actual rollback; original Error remains unwrapped')
    if any(edges[0][0]<=c[1]<edges[0][1]for c in calls):
        raise ValueError('phase port faults never reinterpreted as rollback provider faults')
    if 'if_acmpeq'not in rollback or 'UnconfirmedJmsRollbackException'not in rollback:
        raise ValueError('identity-safe suppressed/typed unconfirmed contract retained')
    isolation=next(v for k,v in table.items()if 'isolateFatal('in k and 'Runnable'in k)
    iso=p.one_call({'isolation':isolation},'Method rollbackAfterFailure:')[0]
    if 'Ljava/lang/Runnable;Ljava/lang/Runnable;)V'not in p.instructions(isolation)[iso[2]][2]:
        raise ValueError('fatal isolation passes both exact synchronous phase ports')
    listeners=[]
    for cls in ('SyncRequestListener','TransactedEventListener','QuestionWorkListener','WebLogListener'):
        blocks=p.methods(read('api',prefix+cls))
        public=[k for k in blocks if ' onMessage('in k and 'Runnable'not in k]
        phase=next(v for k,v in blocks.items()if ' onMessage('in k and 'Runnable'in k)
        if len(public)!=1:raise ValueError('retained two-argument listener entry')
        if cls in ('SyncRequestListener','TransactedEventListener'):
            mode=p.one_call({'phase':phase},'JMSContext.getSessionMode:')[0]
            valid=[at for at,_,arg in p.instructions(phase)if 'Objects.requireNonNull:'in arg and at<mode[1]]
            if len(valid)!=4:raise ValueError('four boundary nulls before session read, distinct from processor result null')
            for token in ('InboundTransactions.rollbackAfterFailure:','InboundTransactions.isolateFatal:'):
                c=p.one_call({'phase':phase},token)[0]
                if 'Ljava/lang/Runnable;Ljava/lang/Runnable;)V'not in p.instructions(phase)[c[2]][2]:
                    raise ValueError('both normal and isolation failures forward phase ports')
        else:
            c=p.one_call({'phase':phase},'TransactedEventListener.onMessage:')[0]
            if 'Ljava/lang/Runnable;Ljava/lang/Runnable;)V'not in p.instructions(phase)[c[2]][2]:
                raise ValueError('wrapper phase forwarding unchanged context/message order')
        listeners.append(dict(owner=cls,legacyEntry=public[0],phaseForwarding=True))
    consumers=[]
    for cls in ('SyncRequestConsumers','QuestionWorkConsumers','WebLogConsumers'):
        text=read('api',prefix+cls);blocks=p.methods(text)
        callbacks=[(k,v)for k,v in blocks.items()if 'lambda$start' in k and 'jakarta.jms.Message)'in k]
        if len(callbacks)!=1:raise ValueError('single exact registered callback implementation')
        name,callback=callbacks[0];ops=p.instructions(callback)
        invoke=p.one_call({name:callback},'Listener.onMessage:')[0]
        sets=[
            (i,at,arg)for i,(at,op,arg)in enumerate(ops)if 'AtomicBoolean.set:'in arg and at<invoke[1]]
        if len(sets)!=2 or any(ops[i-1][1]!='iconst_0'for i,_,_ in sets):
            raise ValueError('exactly two per-delivery false resets before listener dispatch')
        rollback=p.one_call({name:callback},'JMSContext.rollback:')[0]
        cas=[at for i,(at,_,arg)in enumerate(ops)if 'AtomicBoolean.compareAndSet:'in arg and at<rollback[1]
            and i>=3 and ops[i-3][1]=='aload_1' and [ops[i-2][1],ops[i-1][1]]==['iconst_0','iconst_1']]
        if len(cas)!=1 or not any(cas[0]<at<rollback[1]and op=='ifeq'for at,op,_ in ops):
            raise ValueError('direct Error rollback guarded by attempted false-to-true CAS')
        if any('acknowledge:'in arg or 'JMSContext.commit:'in arg for _,_,arg in ops):
            raise ValueError('callback never ACK/commit on unknown completion')
        errors=[t for *_,t in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class ([\w/$]+)\s*$',callback)]
        if not all(t in errors for t in ('java/lang/Error','java/lang/RuntimeException','jakarta/jms/JMSException')):
            raise ValueError('ordinary checked/RTE and fatal paths remain distinct')
        source=p.W/'pg6246-normal-phase-selected-v1/source/src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound'/ (cls+'.java')
        s=source.read_text()
        if not s.index('var rollbackAttempted = new AtomicBoolean();')<s.index('var rollbackConfirmed = new AtomicBoolean();')<s.index('Runnable attemptingRollback')<s.index('Runnable confirmingRollback'):
            raise ValueError('fixed synchronous phase state/ports allocated before owning acquisition')
        if cls=='SyncRequestConsumers' and not s.index('for (int index = 0; index < CONCURRENCY; index++)')<s.index('var rollbackAttempted'):
            raise ValueError('four contexts cannot share one rollback confirmation')
        acquire='JMSContext context = Objects.requireNonNull(factory.get()'if cls=='SyncRequestConsumers'else'new '+cls+'(factory, onUnconfirmed)'
        if not s.index('Runnable confirmingRollback')<s.index(acquire):raise ValueError('phase ports exist before first context acquisition')
        if 'if (!rollbackConfirmed.get())'not in s or 'rollbackAttempted.compareAndSet(false, true)'not in s:
            raise ValueError('ordinary retry requires this-delivery confirmation; Error attempt at most once')
        consumers.append(dict(owner=cls,callback=name,resetOffsets=[v[1]for v in sets],attemptCasOffset=cas[0],rollbackOffset=rollback[1],
            resolvedLambdaBindings=p.resolved_body(callback,read('api',prefix+cls,verbose=True))))
    return dict(rollbackObserverOffsets=[v[1]for v in calls],actualRollbackOffset=action[1],exceptionTable=edges,
        isolationPhaseForwarding=True,listeners=listeners,consumers=consumers,
        independentEvidence='PG6236 red3/PG6246 original113; actual result separately qualified',
        scope='PG_SOURCE_JVM_NOT_ACTUAL_ROOT_NATIVE_OR_PT_ALTERNATIVE')


def runner_source():
    raw=previous.previous.runner_source()
    for before,after in (
        ('PG6208-keeper-faults-qualification-v1','PG6248-normal-phase-qualification-v1'),
        ('pg6208-keeper-faults-qualification-v1','pg6248-normal-phase-qualification-v1'),
        ('(63,20,1667)','(113,28,1667)'),
        ('pg6206-keeper-faults-selected-v1/source','pg6246-normal-phase-selected-v1/source'),
        ('PG6210-keeper-order-v1','PG6242-confirmed-rollback-order-v1'),
        ('    keeper=keeper_review(read,jar)','    keeper=keeper_review(read,jar)\n    webPrimary=web_primary(read)\n    rollback=rollback_review(read)'),
        ('keeperPolicy=keeper,','keeperPolicy=keeper,webPrimaryPolicy=webPrimary,rollbackPolicy=rollback,')):
        if raw.count(before)!=1:raise ValueError('one current113 proof binding '+before)
        raw=raw.replace(before,after,1)
    return raw


def main():
    scope={**vars(previous.previous.profile.prior),'original_source':original_source,
        'normal_primary_policy':previous.previous.profile.normal_primary_policy,
        'keeper_review':previous.current_keeper,'web_primary':previous.web_primary,'rollback_review':rollback_review}
    exec(compile(runner_source(),'<current113 actual source/JVM review>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
