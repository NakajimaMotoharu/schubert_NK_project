"""Inspect original JVM/source ownership; no invocation of Production Main/admission/runtime."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6056_expiry_read_methods import methods
from pg6084_web_factory_order import instructions
from pg6116_http_owner_order import prepared_owner, resolved_body
from pg6184_unstarted_management_qualification import original_source
from classfile_field_flags import fields

PREFIX='dev.codex.schubert.nk.'


def tokens(text):
    pattern=r'//[^\r\n]*|/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][A-Za-z0-9_$]*|[^\s]'
    return [m.group() for m in re.finditer(pattern,text) if not m.group().startswith(('//','/*'))]


def one_call(blocks,token,expected=1):
    found=[(name,ops[i][0],i) for name,body in blocks.items() for ops in [instructions(body)]
           for i,(_,op,arg) in enumerate(ops) if op.startswith('invoke') and token in arg]
    if len(found)!=expected:raise ValueError('exact actual call count '+token)
    return found


def true_release_ports(blocks,expected):
    found=one_call(blocks,'ServiceProcessResources.ownedRelease:',expected)
    for name,_offset,index in found:
        if instructions(blocks[name])[index-1][1]!='iconst_1':
            raise ValueError('native release policy fixed true before ResourceScope acquire')
    if len(one_call(blocks,'ResourceScope.acquire:',expected))!=expected:
        raise ValueError('same number of explicit owned scopes')
    return found


def stop_confirmation(blocks,atomic):
    keys=[k for k in blocks if k.startswith('  void closeWithin(')]
    if len(keys)!=1:raise ValueError('one reviewed management close')
    code=blocks[keys[0]];ops=instructions(code)
    stores={field:[i for i,(_,op,arg) in enumerate(ops) if op=='putfield' and '// Field '+field+':Z' in arg]
            for field in ('serverStopped','closed')}
    if not atomic:
        stores['closed']=[i for i,(_,op,arg) in enumerate(ops) if op=='invokevirtual' and 'AtomicBoolean.set:' in arg
                          and any('// Field closed:' in x[2] for x in ops[max(0,i-3):i])]
    if any(len(v)!=1 for v in stores.values()):raise ValueError('single success cache writes')
    checks=[]
    for field,writes in stores.items():
        at=writes[0]
        guards=[]
        for i,(_,op,arg) in enumerate(ops[:at]):
            if '// Field started:' not in arg or op!='getfield':continue
            branch=i+2 if atomic else i+1
            if branch>=len(ops) or ops[branch][1] not in ('ifeq','ifne'):continue
            target=int(ops[branch][2].strip())
            if field=='serverStopped' and ops[branch][1]=='ifeq' and target>ops[at][0]:guards.append(ops[branch][0])
            if field=='closed' and ops[branch][1]=='ifne' and target<ops[at][0] and target>ops[branch][0] and any(x[1]=='athrow' for x in ops[branch+1:at]):guards.append(ops[branch][0])
        if len(guards)!=1:raise ValueError('normal start guards each actual success cache '+field)
        checks.append(dict(field=field,guardOffset=guards[0],storeOffset=ops[at][0]))
    await_at=one_call({keys[0]:code},'ThreadPoolExecutor.awaitTermination:')[0][1]
    if not await_at<checks[1]['storeOffset']:raise ValueError('actual join precedes closed')
    return checks


def main():
    source=original_source();qp=BASE/'PG6184-unstarted-management-qualification-v1/manifest.json'
    q=json.loads(qp.read_bytes());private=W/'pg6184-unstarted-management-qualification-v1/manifest.safe.json'
    if not (q['source']==source and q['actualExit']==0 and (q['tests'],q['suites'],q['physicalMain'])==(59,20,1667)
            and sha(private)==q['privateManifestSha256']):raise ValueError('original59/source/Jar qualification first')
    proof=json.loads(private.read_bytes());run=W/'pg6182-unstarted-management-selected-v1/source'
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    def jar(module,current=True):
        base=run if current else W/'pg6170-native-retention-selected-v3/source'
        return base/('src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
    def read(module,cls,current=True,verbose=False):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-v' if verbose else '-c','-s',
            '-classpath',str(jar(module,current)),PREFIX+cls],text=True)
    def source_text(module,cls,current=True):
        path='src/schubert-nk-'+module+'/src/main/java/'+PREFIX.replace('.','/')+cls.replace('.','/')+'.java'
        return (run/path).read_text() if current else subprocess.check_output(['git','show','7b6296d5c:'+path],cwd=ROOT,text=True)
    reviews=[]
    for module,cls,atomic in (('api','api.bootstrap.ApiManagementServer',True),('web','web.bootstrap.WebManagementServer',False)):
        body=read(module,cls);blocks=methods(body)
        required=['healthy','information','executor','promoted','promotionAttempted','stopping','stopLock']
        if atomic:required.append('started')
        else:required.append('closed')
        owner=prepared_owner(blocks,PREFIX+cls,required,'$Factory.create:','server')
        with zipfile.ZipFile(jar(module)) as z:flags=fields(z.read((PREFIX+cls).replace('.','/')+'.class'))
        if flags[b'server']['flags']!=0x12 or flags[b'stopLock']['flags']!=0x12:raise ValueError('private final actual owner/lock')
        before=methods(read(module,cls,False))
        public=lambda d:{k for k in d if k.startswith('  public ')}
        if public(before)!=public(blocks):raise ValueError('unchanged public management ABI')
        reviews.append(dict(owner=module+':'+cls,preparedOwner=owner,successCacheGuards=stop_confirmation(blocks,atomic),publicAbiUnchanged=True))
    api=methods(read('api','api.bootstrap.ApiProcessMain'))
    callproof={t:one_call(api,t) for t in ('ApiBrokerContexts.createRetainingUnknown:',
        'ApiApplicationPreparation.executeRetainingUnknown:','ApiManagementServer.bind:','ApiMessagingRuntime.startRetainingUnknown:')}
    for forbidden in ('ApiBrokerContexts.create:','ApiManagementServer.open:','ApiMessagingRuntime.start:'):
        one_call(api,forbidden,0)
    callproof['releasePorts']=true_release_ports(api,3)
    prep=methods(read('api','api.storage.ApiApplicationPreparation'))
    callproof['innerReleasePorts']=true_release_ports(prep,4)
    web=methods(read('web','web.bootstrap.WebNativeRuntime'))
    callproof['webReturnedFactory']=one_call(web,'WebBrokerContexts.createRetainingUnknown:')
    one_call(web,'WebBrokerContexts.create:',0)
    cls='api.storage.ApiApplicationPreparation'
    old,new=[source_text('api',cls,now) for now in (False,True)]
    graph=lambda t:t[t.index('var login ='):t.index('operation.run(Map.copyOf(processors), outbox);')+len('operation.run(Map.copyOf(processors), outbox);')]
    if tokens(graph(old))!=tokens(graph(new)):raise ValueError('all31 handler graph algorithms/IDs/ports unchanged')
    twr=lambda t:t[t.index('try (var codecs ='):t.index('// Package-local component boundary')]
    if tokens(twr(old))!=tokens(twr(new)):raise ValueError('ordinary codec/root TWR/borrowed call unchanged')
    # Normal start is the only reviewed newly changed management method; stop guards above are new.
    unchanged=[]
    for cls in ('api.bootstrap.ApiProcessMain','api.storage.ApiApplicationPreparation'):
        before,after=[methods(read('api',cls,now)) for now in (False,True)]
        exported=lambda d:{k for k in d if k.startswith('  public ')}
        added=exported(after)-exported(before)
        if not exported(before)<=exported(after) or (len(added)!=int(cls.endswith('ApiApplicationPreparation'))):
            raise ValueError('only one specified public native preparation entry added')
        if added and not next(iter(added)).startswith('  public static void executeRetainingUnknown('):raise ValueError('exact native entry only')
        unchanged.append(dict(owner=cls,oldPublicRetained=True,addedPublic=sorted(added)))
    # The close algorithm outside the SS317 start guards remains backed by original real PT.
    management=methods(read('api','api.bootstrap.ApiManagementServer'))
    start=next(v for k,v in management.items() if k=='  void start();')
    ops=instructions(start)
    sequence=[]
    for token in ('ReentrantLock.lock:','HttpServer.setExecutor:','HttpServer.createContext:','HttpServer.start:'):
        sequence.append(one_call({'start':start},token)[0][1])
    if sequence!=sorted(sequence) or start.count('ReentrantLock.unlock:')!=2 or not re.search(r'\d+\s+\d+\s+\d+\s+any',start):
        raise ValueError('start serialized, all setup precedes normal start and compiler finally unlock')
    if not any(op=='putfield' and '// Field startAttempted:Z' in arg for _,op,arg in ops):raise ValueError('one-shot attempt before setup')
    # Resolve actual lambda handles/all bootstrap arguments for the parent and inner resource scopes.
    bindings={}
    for cls in ('api.bootstrap.ApiProcessMain','api.storage.ApiApplicationPreparation'):
        verbose=read('api',cls,verbose=True);blocks=methods(read('api',cls))
        bindings[cls]={k:hashlib.sha256(json.dumps(resolved_body(v,verbose),sort_keys=True).encode()).hexdigest()
            for k,v in blocks.items() if 'InvokeDynamic #' in v}
    value=dict(actualExit=0,source=source,qualificationSha256=sha(qp),ownershipReviewed=True,
        scope='PG_SOURCE_JVM_REVIEW_NOT_REAL_NATIVE_PT_OR_PT_ALTERNATIVE',owners=reviews,callProof=callproof,
        unchanged31HandlerGraph=True,ordinaryTwrPreserved=True,publicAbiReview=unchanged,
        startLockSetupOffsets=sequence,actualLambdaBindingHashes=bindings,
        residualRisks=['unstarted JDK complete resource release not guaranteed; native retains UNKNOWN',
            'real Root/admission/current/cohort safety dependencies held; no actual runtime proof',
            'global coverage/native/CHR/451/trace/formal remain unaccepted'],
        testsExecuted=0,additionalBuildsIssued=0,formalAccepted=False,nativeQualified=False,ptAlternativeCompleted=0)
    os.umask(0o077);out=BASE/'PG6186-native-ownership-order-v1';out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=source,ownershipReviewed=True,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
