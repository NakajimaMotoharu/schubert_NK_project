"""Original63 JVM review, no Production invocation or alternative PT accounting."""
import re
import struct
import zipfile
import pg6195_management_primary_order_v2 as profile
from pg6208_keeper_faults_qualification import original_source
from classfile_field_flags import fields


def keeper_review(read,jar):
    p=profile.prior
    core=p.methods(read('bootstrap','api.file.ServiceProcessResources'))
    pick=lambda part:next(v for k,v in core.items() if part in k)
    held=pick('retainUnknownRelease(java.lang.Throwable, java.lang.Runnable, java.lang.Runnable)')
    ops=p.instructions(held)
    if sum(op=='invokestatic' and 'Objects.requireNonNull:' in arg for _,op,arg in ops)!=3:
        raise ValueError('all three fault ports established before diagnostic')
    edges=re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class (java/lang/\w+)\s*$',held)
    expected=[('21','29','32'),('33','39','42'),('43','49','52')]
    if [(a,b,c) for a,b,c,t in edges]!=[v for v in expected for _ in range(2)] or [t for *_,t in edges]!=['java/lang/RuntimeException','java/lang/Error']*3:
        raise ValueError('diagnostic/tick/fallback each retain both RuntimeException and Error')
    if [(n,arg.strip()) for n,op,arg in ops if op=='goto']!=[(29,'33'),(39,'33'),(49,'54'),(54,'33')]:
        raise ValueError('all post-null successful/caught paths return to same observation loop')
    if any(op.endswith('return') or op=='athrow' for _,op,_ in ops):
        raise ValueError('no explicit normal/exception exit from keeper body')
    fixed=pick('public static void retainUnknownRelease(java.lang.Throwable)')
    if 'Field UNKNOWN_OBSERVATION:' not in fixed or 'Field UNKNOWN_FALLBACK:' not in fixed:
        raise ValueError('native overload fixes both prebuilt ports')
    wait=pick('static void waitUnknownInterval()');w=p.instructions(wait)
    if sum('Thread.interrupted:' in a for _,_,a in w)!=2 or sum('System.nanoTime:' in a for _,_,a in w)!=2:
        raise ValueError('fixed monotonic deadline and pre/during-wait interrupt clearing')
    if [(n,op,a.strip()) for n,op,a in w if op in ('ifle','goto')]!=[(21,'ifle','35'),(32,'goto','12')]:
        raise ValueError('spurious wake/IRQ recheck same fixed deadline')
    if len(p.one_call({'wait':wait},'LockSupport.parkNanos:'))!=1:
        raise ValueError('one standard bounded fallback wait')
    init=pick('static {};')
    for token in ('Field UNKNOWN_OBSERVATION:','Field UNKNOWN_FALLBACK:','LockSupport.parkNanos:'):
        if token not in init:raise ValueError('fixed retaining class initialized before getter returns')
    getter=pick('unknownReleasePolicy()')
    resolved=p.resolved_body(getter,read('bootstrap','api.file.ServiceProcessResources',verbose=True))
    if 'retainUnknownRelease:(Ljava/lang/Throwable;)V' not in str(resolved):
        raise ValueError('actual bootstrap binding points to fixed native overload')
    sites=[]
    targets=(('api','api.messaging.config.ApiBrokerContexts','java/util/function/BiFunction.apply:'),
        ('api','api.messaging.config.ArtemisConnectionFactoryProvider','Method configureOwned:'),
        ('api','api.messaging.inbound.ApiMessagingRuntime','SyncRequestConsumers.start:'),
        ('web','web.messaging.WebBrokerContexts','Method newFactory:'))
    for module,cls,target in targets:
        blocks=p.methods(read(module,cls));calls=p.one_call(blocks,'ServiceProcessResources.unknownReleasePolicy:',2 if module=='web' else 1)
        for name,at,index in calls:
            code=blocks[name];acquire=p.one_call({name:code},target,0 if 'jakarta.jms.ConnectionFactory, java.lang.AutoCloseable, boolean)' in name else (3 if cls.endswith('ApiBrokerContexts') else 1))
            # Web's borrowed constructor owns no acquisition; the endpoint constructor does.
            if not acquire and module!='web':raise ValueError('native prepared acquisition site')
            if acquire and at>=acquire[0][1]:raise ValueError('invokestatic retaining class initialization precedes first acquisition')
            sites.append(dict(owner=module+':'+cls,method=name,getterOffset=at,acquisitionOffsets=[v[1] for v in acquire]))
    # Every changed WebNativeRuntime byte is one of four private-reference access flags.
    oldroot=p.W/'pg6191-management-primary-selected-v2/source'
    oldjar=oldroot/'src/schubert-nk-web/target/schubert-nk-web-0.1.0-SNAPSHOT.jar'
    cls='dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.class'
    with zipfile.ZipFile(oldjar) as z:before=z.read(cls)
    with zipfile.ZipFile(jar('web')) as z:after=z.read(cls)
    old,new=fields(before),fields(after);expected=bytearray(before);flags=[]
    if set(old)!=set(new):raise ValueError('complete unchanged Web field inventory')
    for name in (b'broker',b'codecs',b'transfer',b'assets'):
        a,b=old[name],new[name]
        if a['flags']!=0x42 or b['flags']!=2 or a['offset']!=b['offset'] or a['descriptor']!=b['descriptor']:
            raise ValueError('private volatile reference only to private at same field offset')
        struct.pack_into('>H',expected,a['offset'],2);flags.append(name.decode())
    if bytes(expected)!=after:raise ValueError('all other Web class bytes identical')
    if any(new[n]['flags']!=0x42 for n in (b'replies',b'replay',b'retry',b'http',b'management')):
        raise ValueError('health/ready lock-free publication remains volatile')
    # Inline constant has no executable effect; compare all methods plus resolved lambda bindings.
    def oldread():
        import subprocess
        return subprocess.check_output([str(p.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',
            str(oldroot/'src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'),p.PREFIX+'api.bootstrap.ApiManagementServer'],text=True)
    a=p.methods(oldread());b=p.methods(read('api','api.bootstrap.ApiManagementServer'))
    if a!=b:raise ValueError('API diagnostic literal constant leaves every executable method unchanged')
    return dict(keeperExceptionEdges=edges,loopBackEdges=4,fixedNativePorts=True,monotonicFallback=True,
        preAcquisitionGetterSites=sites,webOnlyFourFieldFlags=flags,webAllOtherClassBytesIdentical=True,
        apiAllExecutableMethodsIdentical=True,testsExecuted=0,vmActions=0,
        residualRisks=['persistent VM/standard wait failure may prevent bounded waiting; no normal cleanup inferred',
            'host child143 is not actual Root/native/ownedstop proof; global coverage not100'])


def runner_source():
    raw=profile.runner_source()
    for before,after in (
        ('PG6193-management-primary-qualification-v2','PG6208-keeper-faults-qualification-v1'),
        ('pg6193-management-primary-qualification-v2','pg6208-keeper-faults-qualification-v1'),
        ('(60,20,1667)','(63,20,1667)'),
        ('pg6191-management-primary-selected-v2/source','pg6206-keeper-faults-selected-v1/source'),
        ('PG6195-management-primary-order-v2','PG6210-keeper-order-v1'),
        ('    value=dict(actualExit=0','    keeper=keeper_review(read,jar)\n    value=dict(actualExit=0'),
        ('ownershipReviewed=True,normalPrimaryPolicy=primary,','ownershipReviewed=True,normalPrimaryPolicy=primary,keeperPolicy=keeper,')):
        if raw.count(before)!=1:raise ValueError('exact current63 binding '+before)
        raw=raw.replace(before,after,1)
    return raw


def main():
    scope={**vars(profile.prior),'original_source':original_source,'normal_primary_policy':profile.normal_primary_policy,'keeper_review':keeper_review}
    exec(compile(runner_source(),'<original63 PG/JVM review>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
