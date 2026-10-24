"""Exact role-context ownership protocol/public metadata/all-six bytes; no product initialization."""
import copy
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='f1b570e45f072b6001ad7e8e250ffbc5686c494a'
BEFORE='3613b2742c8bcda85a2ec889d023307fadf1875c'
COMPILE=host.W/'pg8740-metric-context-six-compile-v1'
SLOT=host.W/'pg8746-metric-context-trace-v1'
OUT=host.BASE/'PG8746-metric-context-trace-v1'
ROLES={'api':'Api','web':'Web'}
MAINS={role:f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}MetricContext.java' for role,title in ROLES.items()}
ADDED=set(MAINS.values())|{path.replace('/main/','/test/').replace('.java','Test.java') for path in MAINS.values()}
CLASSES={role+':dev/codex/schubert/nk/'+role+'/monitoring/'+title+'MetricContext.class' for role,title in ROLES.items()}

def owner(model,role):
    assert model['package']=='dev.codex.schubert.nk.'+role+'.monitoring' and model['type']==ROLES[role]+'MetricContext'
    assert {'io.micrometer.core.instrument.MeterRegistry','java.util.function.Function','java.util.concurrent.locks.ReentrantLock','java.util.concurrent.atomic.AtomicBoolean'}<=set(model['imports'])
    forbidden=tuple('dev.codex.schubert.nk.'+other+'.' for other in ('api','web','batch','bootstrap') if other!=role)
    assert not any(name.startswith(forbidden+('java.net.','java.sql.','java.nio.file.')) for name in model['imports'])

def protocol(compact,role):
    retained='retainedBindings=Optional.of(Objects.requireNonNull(setup.apply(source),"metricbindings"));'
    assert compact.count('customFactory.get()')==compact.count('setup.apply(source)')==compact.count('standard.bind(mode)')==1
    assert compact.index('ownedCustom=Optional.of(')<compact.index(retained)<compact.index('standard.bind(mode)')
    assert compact.count('rejectStopping();')==3
    assert 'new'+ROLES[role]+'CustomMetricPayload().render(ready,mode,borrowed::orElseThrow,standard)' in compact
    close=compact[compact.index('publicvoidclose()'):]
    assert 'if(lock.isHeldByCurrentThread()||!lock.tryLock())' in close
    assert close.index('stopping.set(true);')<close.index('lock.tryLock()')<close.index('standard.close();')<close.index('ownedCustom.ifPresent(MeterRegistry::close);')<close.index('retainedBindings=Optional.empty();')<close.index('ownedCustom=Optional.empty();')<close.index('closed=true;')
    assert close.index('initialized=false;')<close.index('standard.close();') and 'finally{lock.unlock();}' in close
    assert 'catch(' not in compact
    recipe='newExactDurationMeterRegistry(io.micrometer.core.instrument.simple.SimpleConfig.DEFAULT,io.micrometer.core.instrument.Clock.SYSTEM)' if role=='api' else 'newOverflowSafeHttpMeterRegistry(io.micrometer.core.instrument.Clock.SYSTEM)'
    assert recipe in compact

def metadata(text,role):
    qualified='dev.codex.schubert.nk.'+role+'.monitoring.'
    name=ROLES[role]+'MetricContext'
    lines=[line for line in text.splitlines() if line.strip()]
    assert lines[:2]==['Compiled from "'+name+'.java"','public final class '+qualified+name+'<T> implements java.lang.AutoCloseable {']
    fields=[(line,lines[i+1]) for i,line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    assert len(fields)==14 and all(line.startswith('  private ') for line,_ in fields)
    names={re.search(r' ([A-Za-z_]\w*)(?: = .*)?;$',line).group(1) for line,_ in fields}
    assert names=={'INITIALIZATION_UNAVAILABLE','CLOSE_UNCONFIRMED','lock','stopping','mode','detailed','setup','customFactory','standard','ownedCustom','retainedBindings','attempted','initialized','closed'}
    assert ('  private java.util.Optional<T> retainedBindings;','    descriptor: Ljava/util/Optional;') in fields
    assert ('  private final java.util.concurrent.locks.ReentrantLock lock;','    descriptor: Ljava/util/concurrent/locks/ReentrantLock;') in fields
    assert ('  private final '+qualified+ROLES[role]+'StandardMetricSource standard;','    descriptor: L'+qualified.replace('.','/')+ROLES[role]+'StandardMetricSource;') in fields
    assert ('  private static final java.lang.String CLOSE_UNCONFIRMED = "metric context close unconfirmed";','    descriptor: Ljava/lang/String;') in fields
    public=[line.strip() for line in lines if line.startswith('  public ') and line.endswith(';')]
    assert public==['public '+qualified+name+'(java.lang.String, java.util.function.Function<? super io.micrometer.core.instrument.MeterRegistry, ? extends T>);','public void initialize();','public java.util.Optional<T> bindings();','public java.lang.String render(boolean);','public void close();']
    return dict(fields=fields,publicApi=public,directSdkGetter=False,bindingsAreBorrowedMetadataNotWholeDataCertification=True)

if __name__=='__main__':
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
        'normal':('PG8740-metric-context-six-compile-v1/manifest.json','45fda0573fcd8709921be8374a6c77bbb598c7a51dab7b6faa9eb01c3fda3aff'),
        'current':('PG8744-metric-context-post-v1/manifest.json','967efc86c98f8574eaef4b3f625ae4024c2d8dfc33899a74b8e3ba76e2891141'),
        'priorNormal':('PG8722-full-metric-payload-six-compile-v1/manifest.json','2cb763db0522c0bcc083c86585505d8dbec51e19700b7019c55548ca03a4c63e'),
        'priorTrace':('PG8728-full-metric-payload-trace-v1/manifest.json','28d74c1c33213ea6c74e7fb0d7793f1bf71180632cb16d646797ea824793dd43'),
        'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
        'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in witnesses.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current,prior=proof['normal'],proof['current'],proof['priorNormal']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==52 and current['suites']==2 and len(current['executableClasses'])==2 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert prior['source']==proof['priorTrace']['source']==BEFORE
    before,after=prior['begin']['inputHashes'],normal['begin']['inputHashes']
    assert set(after)-set(before)==ADDED and not(set(before)-set(after)) and all(after[path]==digest for path,digest in before.items())
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    previous,physical=base.inventory(prior),base.inventory(normal)
    assert len(previous)==1828 and len(physical)==1830 and set(physical)-set(previous)==CLASSES and all(physical[path]==digest for path,digest in previous.items())
    original=proof['original']['allPhysicalMainSha256']
    assert len(original)==1669 and all(physical[path]==digest for path,digest in original.items())
    for path,digest in current['physicalClasses'].items():
        role=next(role for role in ROLES if path.startswith('dev/codex/schubert/nk/'+role+'/'))
        assert physical[role+':'+path]==digest
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}==dict.fromkeys(ADDED,'A')
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==213 and not(set(old_rows)&ADDED)
    rows=[]
    for path in sorted(set(old_rows)|ADDED):
        digest=host.sha(snapshot/path)
        assert path in ADDED or old_rows[path]['sha256']==digest
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_CALLER_HELD_CONTEXT_SOURCE' if path in ADDED else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'))
    assert len(rows)==217
    models={};role_negatives=[];protocol_negatives=[]
    for role,path in MAINS.items():
        body=(snapshot/path).read_text();compact=''.join(body.split())
        model=contract.java(body);owner(model,role);protocol(compact,role);models[role]=model
        for name,mutate in (('wrong-role',lambda r:r.update(package='dev.codex.schubert.nk.batch.monitoring')),('bootstrap-owner',lambda r:r['imports'].append('dev.codex.schubert.nk.bootstrap.metric.Forbidden')),('network-authority',lambda r:r['imports'].append('java.net.ServerSocket'))):
            changed=copy.deepcopy(model);mutate(changed)
            try:owner(changed,role)
            except AssertionError:role_negatives.append(role+':'+name)
            else:raise AssertionError('every role mutation rejects')
        retain='retainedBindings=Optional.of(Objects.requireNonNull(setup.apply(source),"metricbindings"));'
        for name,changed in (('drop-strong-bindings',compact.replace(retain,'setup.apply(source);',1)),('reverse-close-order',compact.replace('standard.close();ownedCustom.ifPresent(MeterRegistry::close);','ownedCustom.ifPresent(MeterRegistry::close);standard.close();',1)),('non-acquiring-close',compact.replace('lock.tryLock()','lock.isLocked()',1)),('missing-stop-signal',compact.replace('stopping.set(true);','',1))):
            assert changed!=compact
            try:protocol(changed,role)
            except (AssertionError,ValueError):protocol_negatives.append(role+':'+name)
            else:raise AssertionError('every ownership protocol mutation rejects')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    field_rows={};field_negatives=[]
    for role,path in MAINS.items():
        compiled_class=snapshot/path.replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s','-constants',str(compiled_class)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        actual=metadata(text,role)
        ctor='  dev.codex.schubert.nk.'+role+'.monitoring.'+ROLES[role]+'MetricContext(java.lang.String, java.util.function.Function'
        for name,changed in (('public-stop-flag',text.replace('private final java.util.concurrent.atomic.AtomicBoolean stopping;','public final java.util.concurrent.atomic.AtomicBoolean stopping;',1)),('weak-bindings',text.replace('private java.util.Optional<T> retainedBindings;','private java.util.Optional<java.lang.ref.WeakReference<T>> retainedBindings;',1)),('public-registry-getter',text.replace('\n}','\n  public io.micrometer.core.instrument.MeterRegistry getRegistry();\n}')),('public-test-constructor',text.replace(ctor,'  public '+ctor.strip(),1)),('false-close-confirmation',text.replace('CLOSE_UNCONFIRMED = "metric context close unconfirmed"','CLOSE_UNCONFIRMED = "metric context closed"',1))):
            assert changed!=text
            try:metadata(changed,role)
            except AssertionError:field_negatives.append(role+':'+name)
            else:raise AssertionError('every field/API mutation rejects')
        code_receipt,code=steps.step(role+'-lock-stop-bytecode',[str(architecture.JAVA.with_name('javap')),'-p','-c',str(compiled_class)])
        assert code_receipt['actualExit']==0 and not code_receipt['timedOut'] and code.count('ReentrantLock.lock:()V')==3 and code.count('ReentrantLock.tryLock:()Z')==1 and code.count('ReentrantLock.isHeldByCurrentThread:()Z')==1 and code.count('ReentrantLock.unlock:()V')>=4 and code.count('AtomicBoolean.set:(Z)V')==1 and 'monitorenter' not in code
        field_rows[role]=dict(metadata=actual,receipt=receipt,lockStopReceipt=code_receipt)
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1830 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation)
    OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1830,physicalAdded=sorted(CLASSES),physicalRemoved=[],physicalChanged={},previousPhysicalUnchanged=1828,originalPhysicalUnchanged=1669,sourceRows=rows,sourceCount=217,currentTests=52,currentSuites=2,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],ownerGuardBinding=dict(models=models,roleNegatives=role_negatives,protocolNegatives=protocol_negatives,fieldNegatives=field_negatives,roleFields=field_rows,bootstrapSourcesUnchanged=34),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,physical=1830,sourceOwners=217,roleNegatives=len(role_negatives),protocolNegatives=len(protocol_negatives),fieldNegatives=len(field_negatives),architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))
