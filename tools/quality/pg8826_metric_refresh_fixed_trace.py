"""Same-source refresh104/four scopes and whole physical bytes; no actual manager/native."""
import copy
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import pg8746_metric_context_trace as old_context
from host_tool_invocation import capture,verify

host,architecture,steps=old_context.host,old_context.architecture,old_context.steps
SOURCE='32041eafe19116bba7b90431f522371f0bcd8d53'
BEFORE='84ee59a95cf4911b40635240a29fe1d8c71cdaf5'
COMPILE=host.W/'pg8820-metric-refresh-fixed-six-compile-v1'
SLOT=host.W/'pg8826-metric-refresh-fixed-trace-v1'
OUT=host.BASE/'PG8826-metric-refresh-fixed-trace-v1'
NORMAL_SHA='8107b7e202b684ba02a3fedda816ef40f3a4dcb1fbe7dd7fb785508b6d4c3d54'
CURRENT_SHA='bbacc38eab6910f114c63829eb68f65c435ec6cdf4b5da211a0289e8a0b805ca'
ROLES=old_context.ROLES
MAINS=old_context.MAINS
CONTEXT_UNITS={role:path.replace('/main/','/test/').replace('.java','Test.java') for role,path in MAINS.items()}
HTTP_UNITS={role:f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{title}MetricHttpHandlerTest.java' for role,title in ROLES.items()}
CHANGED=set(MAINS.values())|set(CONTEXT_UNITS.values())|set(HTTP_UNITS.values())
CLASSES=old_context.CLASSES
MANAGER_CLASSES={role+':dev/codex/schubert/nk/'+role+'/bootstrap/'+title+'ManagementServer.class' for role,title in ROLES.items()}

def sampler_contract(compact,role):
    assert compact.count('customFactory.get()')==compact.count('setup.apply(source)')==compact.count('standard.bind(mode)')==1
    assert 'Optional.<Consumer<?superT>>of(Objects.requireNonNull(refresh,"metricmetadatarefresh"))' in compact
    assert 'this.refresh=Objects.requireNonNull(refresh,"metricrefreshholder");' in compact
    assert 'this(mode,setup,Optional.empty(),customFactory,standard);' in compact
    render=compact[compact.index('publicStringrender(booleanready)'):compact.index('privatevoidrejectStopping()')]
    sample='if(detailed&&refresh.isPresent()){refresh.orElseThrow().accept(retainedBindings.orElseThrow());rejectStopping();}'
    assert render.count(sample)==1 and render.index('requireRunning();')<render.index(sample)<render.index('varborrowed=ownedCustom;')
    assert 'lock.lock();' in render and 'finally{lock.unlock();}' in render
    assert 'catch(' not in compact and compact.count('rejectStopping();')==4
    assert 'new'+ROLES[role]+'CustomMetricPayload().render(ready,mode,borrowed::orElseThrow,standard)' in render
    close=compact[compact.index('@Overridepublicvoidclose()'):]
    assert close.index('stopping.set(true);')<close.index('lock.tryLock()')<close.index('standard.close();')<close.index('ownedCustom.ifPresent(MeterRegistry::close);')
    recipe='newExactDurationMeterRegistry(io.micrometer.core.instrument.simple.SimpleConfig.DEFAULT,io.micrometer.core.instrument.Clock.SYSTEM)' if role=='api' else 'newOverflowSafeHttpMeterRegistry(io.micrometer.core.instrument.Clock.SYSTEM)'
    assert compact.count(recipe)==2

def metadata(text,role):
    q='dev.codex.schubert.nk.'+role+'.monitoring.'
    name=ROLES[role]+'MetricContext'
    lines=[line for line in text.splitlines() if line.strip()]
    fields=[(line,lines[i+1]) for i,line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    assert len(fields)==15 and all(line.startswith('  private ') for line,_ in fields)
    names={re.search(r' ([A-Za-z_]\w*)(?: = .*)?;$',line).group(1) for line,_ in fields}
    assert names=={'INITIALIZATION_UNAVAILABLE','CLOSE_UNCONFIRMED','lock','stopping','mode','detailed','setup','refresh','customFactory','standard','ownedCustom','retainedBindings','attempted','initialized','closed'}
    assert ('  private final java.util.Optional<java.util.function.Consumer<? super T>> refresh;','    descriptor: Ljava/util/Optional;') in fields
    assert ('  private java.util.Optional<T> retainedBindings;','    descriptor: Ljava/util/Optional;') in fields
    public=[line.strip() for line in lines if line.startswith('  public ') and line.endswith(';')]
    assert public==['public '+q+name+'(java.lang.String, java.util.function.Function<? super io.micrometer.core.instrument.MeterRegistry, ? extends T>);','public '+q+name+'(java.lang.String, java.util.function.Function<? super io.micrometer.core.instrument.MeterRegistry, ? extends T>, java.util.function.Consumer<? super T>);','public void initialize();','public java.util.Optional<T> bindings();','public java.lang.String render(boolean);','public void close();']
    return dict(fieldNames=sorted(names),publicApi=public)

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
      'normal':('PG8820-metric-refresh-fixed-six-compile-v1/manifest.json',NORMAL_SHA),
      'current':('PG8824-metric-refresh-fixed-post-v1/manifest.json',CURRENT_SHA),
      'priorNormal':('PG8784-management-metric-fixed-six-compile-v1/manifest.json','c2b565fd275d8a1bccd79cfa9ebf123809e3ad429190d37df2b6711caa244df7'),
      'priorTrace':('PG8790-management-metric-fixed-trace-v1/manifest.json','b53058401d0e5a62d2df2e66f2291c5a9c32f6d2086f2be5a62afbf6c5f7de81'),
      'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in witnesses.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current,prior=proof['normal'],proof['current'],proof['priorNormal']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==104 and current['suites']==4 and len(current['executableClasses'])==4 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert prior['source']==proof['priorTrace']['source']==BEFORE
    before,after=prior['begin']['inputHashes'],normal['begin']['inputHashes']
    assert set(before)==set(after) and {path for path in before if before[path]!=after[path]}==CHANGED
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    previous,physical=old_context.base.inventory(prior),old_context.base.inventory(normal)
    assert len(previous)==len(physical)==1832 and set(previous)==set(physical)
    assert {path for path,digest in previous.items() if physical[path]!=digest}==CLASSES
    original=proof['original']['allPhysicalMainSha256']
    assert len(original)==1669 and {path for path,digest in original.items() if physical[path]!=digest}==MANAGER_CLASSES
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}==dict.fromkeys(CHANGED,'M')
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==223 and CHANGED<=set(old_rows)
    rows=[]
    for path in sorted(old_rows):
        digest=host.sha(snapshot/path)
        assert path in CHANGED or old_rows[path]['sha256']==digest
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_REFRESH_SCOPE_OR_SELECTED_CONSUMER_TEST' if path in CHANGED else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'))
    role_negatives=[];protocol_negatives=[];models={};preserved_tests={}
    for role,path in MAINS.items():
        body=(snapshot/path).read_text();compact=''.join(body.split())
        model=old_context.contract.java(body);old_context.owner(model,role);sampler_contract(compact,role);models[role]=model
        old=subprocess.check_output(['git','show',BEFORE+':'+path],cwd=host.ROOT,text=True)
        previous_compact=''.join(old.split())
        begin='publicvoidinitialize()';end='publicOptional<T>bindings()'
        assert compact[compact.index(begin):compact.index(end)]==previous_compact[previous_compact.index(begin):previous_compact.index(end)]
        close='@Overridepublicvoidclose()'
        assert compact[compact.index(close):]==previous_compact[previous_compact.index(close):]
        for name,mutate in (('wrong-role',lambda m:m.update(package='dev.codex.schubert.nk.batch.monitoring')),('network-authority',lambda m:m['imports'].append('java.net.ServerSocket'))):
            changed=copy.deepcopy(model);mutate(changed)
            try: old_context.owner(changed,role)
            except AssertionError: role_negatives.append(role+':'+name)
            else: raise AssertionError('every role mutation rejects')
        for name,changed in (('standard-callback',compact.replace('if(detailed&&refresh.isPresent())','if(refresh.isPresent())',1)),('missing-stop-recheck',compact.replace('accept(retainedBindings.orElseThrow());rejectStopping();','accept(retainedBindings.orElseThrow());',1)),('lost-binding',compact.replace('accept(retainedBindings.orElseThrow())','accept(null)',1)),('lost-optional-type',compact.replace('Optional.<Consumer<?superT>>of','Optional.of',1))):
            assert changed!=compact
            try: sampler_contract(changed,role)
            except (AssertionError,ValueError): protocol_negatives.append(role+':'+name)
            else: raise AssertionError('every sampler mutation rejects')
        ctx_test=(snapshot/CONTEXT_UNITS[role]).read_text()
        old_ctx_test=subprocess.check_output(['git','show',BEFORE+':'+CONTEXT_UNITS[role]],cwd=host.ROOT,text=True)
        marker='  /** 1823/PG-D620 '+role.upper()+'MCTX027'
        assert old_ctx_test.endswith('}\n') and ctx_test[:ctx_test.index(marker)].rstrip()==old_ctx_test[:-2].rstrip()
        http_test=(snapshot/HTTP_UNITS[role]).read_text()
        old_http_test=subprocess.check_output(['git','show',BEFORE+':'+HTTP_UNITS[role]],cwd=host.ROOT,text=True)
        new_begin=http_test.index('  @Test\n  void '+role+'mhttp019')
        next_begin=http_test.index('  private static '+ROLES[role]+'MetricContext<String> standard()')
        assert http_test[:new_begin]+http_test[next_begin:]==old_http_test
        preserved_tests[role]=dict(contextOld26BodiesUnchanged=True,httpOld18BodiesUnchanged=True)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    fields={};field_negatives=[]
    for role,path in MAINS.items():
        file=snapshot/path.replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-context-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s','-constants',str(file)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        fields[role]=dict(metadata=metadata(text,role),receipt=receipt)
        for name,changed in (('public-sampler',text.replace('private final java.util.Optional<java.util.function.Consumer<? super T>> refresh;','public final java.util.Optional<java.util.function.Consumer<? super T>> refresh;',1)),('public-registry-getter',text.replace('\n}','\n  public io.micrometer.core.instrument.MeterRegistry registry();\n}'))):
            assert changed!=text
            try: metadata(changed,role)
            except AssertionError: field_negatives.append(role+':'+name)
            else: raise AssertionError('every field mutation rejects')
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1832 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1832,physicalAdded=[],physicalRemoved=[],physicalChanged={path:dict(before=previous[path],after=physical[path]) for path in sorted(CLASSES)},previousPhysicalUnchanged=1830,originalPhysicalUnchanged=1667,previousManagerPhysicalUnchanged=True,sourceRows=rows,sourceCount=223,currentTests=104,currentSuites=4,newTests=16,necessaryModifiedSourceRegression=88,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],ownerGuardBinding=dict(models=models,roleNegatives=role_negatives,protocolNegatives=protocol_negatives,fieldNegatives=field_negatives,fields=fields,preservedOldTestBodies=preserved_tests),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,managerDynamicPt='UNRUN_HOLD',managerCoverage=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,physical=1832,sourceOwners=223,roleNegatives=len(role_negatives),samplerNegatives=len(protocol_negatives),fieldNegatives=len(field_negatives),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
