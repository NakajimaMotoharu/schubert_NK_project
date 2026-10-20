"""Current64 original JVM/source review; finite actions and both non-returning entry loops."""
import inspect
import re
import pg6210_keeper_order as previous
from pg6232_web_cleanup_qualification import original_source
from jvm_monitor_release import local_slot


def exception_edges(code):
    return [(int(a),int(b),int(c),t)for a,b,c,t in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class (java/lang/\w+)\s*$',code)]


def loop_entry(blocks,signature,fixed):
    p=previous.profile.prior
    name=next(k for k in blocks if signature in k);code=blocks[name];ops=p.instructions(code)
    diagnostic=p.one_call({name:code},'Method diagnoseUnknownRelease:')[0][1]
    tick=p.one_call({name:code},'Method observeUnknownInterval:')[0][1]
    back=[(at,int(arg.strip())) for at,op,arg in ops if op=='goto']
    if len(back)!=1 or not diagnostic<back[0][1]<tick<back[0][0]:raise ValueError('diagnostic once then own infinite tick backedge')
    if any(op.endswith('return')or op=='athrow'or op.startswith('if')for _,op,_ in ops):raise ValueError('no native/test keeper normal exit or conditional completion')
    if fixed and any('Field '+field+':' not in code for field in ('UNKNOWN_OBSERVATION','UNKNOWN_FALLBACK')):
        raise ValueError('native entry uses only preinitialized fixed ports')
    if not fixed and sum('Objects.requireNonNull:' in arg for _,_,arg in ops)!=3:
        raise ValueError('three fault inputs validated before diagnosis')
    return dict(method=name,diagnosticOffset=diagnostic,tickOffset=tick,backedge=back[0],noNormalReturn=True,fixedPorts=fixed)


def current_keeper(read,jar):
    p=previous.profile.prior
    core=p.methods(read('bootstrap','api.file.ServiceProcessResources'))
    loops=[loop_entry(core,'public static void retainUnknownRelease(java.lang.Throwable)',True),
        loop_entry(core,'retainUnknownRelease(java.lang.Throwable, java.lang.Runnable, java.lang.Runnable)',False)]
    helpers={key:next(v for k,v in core.items()if key in k)for key in ('diagnoseUnknownRelease(','observeUnknownInterval(')}
    facts={}
    for key,code in helpers.items():
        edges=exception_edges(code);count=1 if key.startswith('diagnose')else 2
        if [t for *_,t in edges]!=['java/lang/RuntimeException','java/lang/Error']*count:
            raise ValueError('each finite action contains both RTE/Error')
        if any(edges[i][:3]!=edges[i+1][:3]for i in range(0,len(edges),2)):
            raise ValueError('both fault classes use same intended protected region')
        if any(op=='athrow'for _,op,_ in p.instructions(code))or not any(op=='return'for _,op,_ in p.instructions(code)):
            raise ValueError('finite action returns to owning loop, not an UNKNOWN cleanup receipt')
        token='PrintStream.println:'if count==1 else 'java/lang/Runnable.run:'
        calls=p.one_call({'action':code},token,count)
        if any(not edges[i*2][0]<=call[1]<edges[i*2][1]for i,call in enumerate(calls)):
            raise ValueError('every diagnostic/tick/fallback invocation inside exact protection')
        if count==1 and ('// String service resource release unconfirmed' not in code or 'Throwable.get' in code):
            raise ValueError('fixed diagnostic only, never raw failure text')
        facts[key]=dict(exceptionEdges=edges,protectedCallOffsets=[c[1]for c in calls])
    wait=next(v for k,v in core.items()if 'waitUnknownInterval()'in k);ops=p.instructions(wait)
    if sum('System.nanoTime:'in a for _,_,a in ops)!=2 or sum('Thread.interrupted:'in a for _,_,a in ops)!=2:
        raise ValueError('one fixed monotonic deadline plus per-loop IRQ clearing')
    p.one_call({'wait':wait},'LockSupport.parkNanos:')
    if sum(op=='goto'for _,op,_ in ops)!=1 or sum(op.startswith('if')for _,op,_ in ops)!=1:
        raise ValueError('same deadline recheck; one finite expiry exit, no deadline extension')
    init=next(v for k,v in core.items()if 'static {}'in k)
    if any(t not in init for t in ('Field UNKNOWN_OBSERVATION:','Field UNKNOWN_FALLBACK:','LockSupport.parkNanos:')):
        raise ValueError('fixed ports and standard wait prepared during class initialization')
    getter=next(v for k,v in core.items()if 'unknownReleasePolicy()'in k)
    if 'retainUnknownRelease:(Ljava/lang/Throwable;)V'not in str(p.resolved_body(getter,read('bootstrap','api.file.ServiceProcessResources',verbose=True))):
        raise ValueError('real getter method handle binds fixed native own-loop entry')
    raw=inspect.getsource(previous.keeper_review)
    start=raw.index('    sites=[]');end=raw.index('    return dict(',start)
    body='def additional(read,jar):\n    p=profile.prior\n'+raw[start:end]+"    return dict(preAcquisitionGetterSites=sites,webFourFlags=flags,apiMethodsUnchanged=True)\n"
    scope=vars(previous).copy();exec(compile(body,'<unchanged explicit getter/flags/ABI facts>','exec'),scope)
    extra=scope['additional'](read,jar)
    return dict(loops=loops,finiteActions=facts,fixedMonotonicFallback=True,**extra)


def web_primary(read):
    p=previous.profile.prior
    blocks=p.methods(read('web','web.bootstrap.WebManagementServer'))
    code=next(v for k,v in blocks.items()if ' open('in k and '$Factory)'in k);ops=p.instructions(code)
    ctors=[i for i,(_,op,arg)in enumerate(ops)if op=='invokespecial'and'java/io/IOException."<init>":(Ljava/lang/String;)'in arg]
    if len(ctors)!=1:raise ValueError('one prebuilt fixed Web IOException, not a provider graph')
    slot=local_slot(ops[ctors[0]+1][1],ops[ctors[0]+1][2],'astore')
    bind=p.one_call({'open':code},'Method bind:')[0][2]
    suppressed=p.one_call({'open':code},'Throwable.addSuppressed:',2)
    fixed=[c for c in suppressed if local_slot(ops[c[2]-1][1],ops[c[2]-1][2],'aload')==slot]
    if len(fixed)!=1 or not ctors[0]<bind<fixed[0][2]:raise ValueError('only unchecked secondary uses exact pre-acquire fixed marker')
    if sum(op=='instanceof'and'// class java/lang/Error'in a for _,op,a in ops)!=2 or sum(op=='if_acmpeq'for _,op,_ in ops)!=1:
        raise ValueError('fatal-secondary priority and identity self-suppression guard')
    if sum(op=='athrow'for _,op,_ in ops)!=2:raise ValueError('separate retained-primary and fatal-secondary exits')
    source=previous.profile.prior.W/'pg6230-web-cleanup-selected-v1/source/src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java'
    old=previous.profile.prior.W/'pg6206-keeper-faults-selected-v1/source/src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java'
    fragment='catch (IOException closing) {\n        failure.addSuppressed(closing);\n'
    if fragment not in source.read_text()or fragment not in old.read_text():raise ValueError('old checked IOException suppressed contract unchanged')
    return dict(fixedDiagnosticLocal=slot,preAcquire=True,checkedIoContractUnchanged=True,fatalPriority=True,selfSuppressionGuard=True,testId='PT-WEB-READY007/eight independent inputs')


def main():
    raw=previous.runner_source()
    for before,after in (
        ('PG6208-keeper-faults-qualification-v1','PG6232-web-cleanup-qualification-v1'),
        ('pg6208-keeper-faults-qualification-v1','pg6232-web-cleanup-qualification-v1'),
        ('(63,20,1667)','(64,20,1667)'),
        ('pg6206-keeper-faults-selected-v1/source','pg6230-web-cleanup-selected-v1/source'),
        ('PG6210-keeper-order-v1','PG6234-web-keeper-order-v1'),
        ('    keeper=keeper_review(read,jar)','    keeper=keeper_review(read,jar)\n    webPrimary=web_primary(read)'),
        ('keeperPolicy=keeper,','keeperPolicy=keeper,webPrimaryPolicy=webPrimary,')):
        if raw.count(before)!=1:raise ValueError('one actual current64 proof binding '+before)
        raw=raw.replace(before,after,1)
    scope={**vars(previous.profile.prior),'original_source':original_source,'normal_primary_policy':previous.profile.normal_primary_policy,
        'keeper_review':current_keeper,'web_primary':web_primary}
    exec(compile(raw,'<current64 real original JVM review>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
