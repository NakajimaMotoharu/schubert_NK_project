"""Changed managers PG/source review and all-six physical metadata. No manager PT or runtime."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8768_metric_http_fixed_trace as prior_tool
from host_tool_invocation import capture,verify

host,architecture,steps=prior_tool.host,prior_tool.architecture,prior_tool.steps
SOURCE='84ee59a95cf4911b40635240a29fe1d8c71cdaf5'
BEFORE='db9c16e0360d7eeb76850feea93899d7a7f8753f'
COMPILE=host.W/'pg8784-management-metric-fixed-six-compile-v1'
SLOT=host.W/'pg8790-management-metric-fixed-trace-v1'
OUT=host.BASE/'PG8790-management-metric-fixed-trace-v1'
NORMAL_SHA='c2b565fd275d8a1bccd79cfa9ebf123809e3ad429190d37df2b6711caa244df7'
CURRENT_SHA='082e7f9f143c8012fc3320d24eb88475b3ff2d236f9ed52f1960b2a38df7e1dc'
ROLES=prior_tool.ROLES
MAINS=prior_tool.MAINS
MANAGERS={role:f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{title}ManagementServer.java' for role,title in ROLES.items()}
HANDLER_FILES=prior_tool.ADDED
CHANGED=HANDLER_FILES|set(MANAGERS.values())
MANAGER_CLASSES={role+':dev/codex/schubert/nk/'+role+'/bootstrap/'+title+'ManagementServer.class' for role,title in ROLES.items()}
CHANGED_CLASSES=prior_tool.CLASSES|MANAGER_CLASSES

def manager_contract(body,role,old):
    title=ROLES[role]
    compact=''.join(body.split());previous=''.join(old.split())
    assert 'privatefinalOptional<'+title+'MetricHttpHandler>metricHandler;' in compact
    assert 'varborrowed=Optional.<'+title+'MetricContext<?>>of(Objects.requireNonNull(context,"borrowedmetriccontext"));' in compact
    assert 'returnnew'+title+'ManagementServer(healthy,json,port,factory,Optional.empty());' in compact
    ctor=compact[compact.index('private'+title+'ManagementServer('):compact.index('privatestaticStringpublicJson(')]
    assert 'this.metricHandler=context.map(value->new'+title+'MetricHttpHandler(value,this::ready));' in ctor
    assert ctor.index('this.metricHandler=')<ctor.index('this.server=Objects.requireNonNull(factory.create(address,32)')
    assert 'context.close(' not in ctor and 'context.initialize(' not in ctor
    assert 'newInetSocketAddress("127.0.0.1",port)' in ctor
    begin='privatestaticStringpublicJson(';end='privatevoidrespond('
    assert compact[compact.index(begin):compact.index(end)]==previous[previous.index(begin):previous.index(end)]
    suffix='@Overridepublicvoidclose()'
    assert compact[compact.index(suffix):]==previous[previous.index(suffix):]
    delegation='if(metricHandler.isPresent()&&METRICS_PATH.equals(path)){metricHandler.orElseThrow().write(exchange);return;}'
    assert compact.count(delegation)==1
    old_response=previous[previous.index(end):previous.index(suffix)]
    new_response=compact[compact.index(end):compact.index(suffix)]
    assert new_response.replace(delegation,'',1)==old_response
    port='8091' if role=='api' else '8081'
    assert 'returnbind(information,healthy,'+port+',HttpServer::create,context);' in compact
    return dict(type=title+'ManagementServer',legacyResponseExceptDelegationUnchanged=True,readyInfoStopUnchanged=True,fixedLoopback=True,handlerBeforeServerFactory=True,callerRetainsContext=True,dynamicPt='UNRUN_HOLD_NOT_EXEMPTED',measuredCoverage=None)

def handler_metadata(text,role):
    qualified='dev.codex.schubert.nk.'+role+'.monitoring.'
    title=ROLES[role]
    lines=[line for line in text.splitlines() if line.strip()]
    fields=[(line,lines[i+1]) for i,line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    assert len(fields)==5 and all(line.startswith('  private ') for line,_ in fields)
    public=[line.strip() for line in lines if line.startswith('  public ') and line.endswith(';')]
    assert public==['public '+qualified+title+'MetricHttpHandler('+qualified+title+'MetricContext<?>, java.util.function.BooleanSupplier);','public void handle(com.sun.net.httpserver.HttpExchange) throws java.io.IOException;','public void write(com.sun.net.httpserver.HttpExchange) throws java.io.IOException;']
    assert ('  private static final java.lang.String PATH = "/actuator/prometheus";','    descriptor: Ljava/lang/String;') in fields
    return dict(privateFields=fields,publicApi=public)

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
        'normal':('PG8784-management-metric-fixed-six-compile-v1/manifest.json',NORMAL_SHA),
        'current':('PG8788-management-metric-fixed-post-v1/manifest.json',CURRENT_SHA),
        'priorNormal':('PG8762-metric-http-fixed-six-compile-v1/manifest.json','1adea2b83c203ffaf1b7398f517ca9dede9e6642ea21e25ead12dac922e45912'),
        'priorTrace':('PG8768-metric-http-fixed-trace-v1/manifest.json','4a763bd2e798bb1af42546d4572ba24e1d82a0c217fd29dc91e052b92e4cc5a4'),
        'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
        'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in witnesses.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current,previous=proof['normal'],proof['current'],proof['priorNormal']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==36 and current['suites']==2 and len(current['executableClasses'])==2 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert previous['source']==proof['priorTrace']['source']==BEFORE
    before,after=previous['begin']['inputHashes'],normal['begin']['inputHashes']
    assert set(before)==set(after) and {path for path in before if before[path]!=after[path]}==CHANGED
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    old_physical,physical=prior_tool.base.inventory(previous),prior_tool.base.inventory(normal)
    changed={path for path in old_physical if physical[path]!=old_physical[path]}
    assert len(old_physical)==len(physical)==1832 and set(old_physical)==set(physical) and changed==CHANGED_CLASSES
    original=proof['original']['allPhysicalMainSha256']
    original_changed={path for path,digest in original.items() if physical[path]!=digest}
    assert len(original)==1669 and original_changed==MANAGER_CLASSES
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}==dict.fromkeys(CHANGED,'M')
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==221 and HANDLER_FILES<=set(old_rows) and not(set(MANAGERS.values())&set(old_rows))
    rows=[]
    for path in sorted(set(old_rows)|set(MANAGERS.values())):
        digest=host.sha(snapshot/path)
        assert path in CHANGED or old_rows[path]['sha256']==digest
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='MANAGER_PG_ONLY_DYNAMIC_PT_UNRUN_HOLD' if path in MANAGERS.values() else 'CURRENT_HTTP_WRITE_SCOPE' if path in HANDLER_FILES else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'))
    assert len(rows)==223
    manager_rows={};manager_negatives=[];role_negatives=[];protocol_negatives=[]
    for role,path in MAINS.items():
        body=(snapshot/path).read_text();compact=''.join(body.split())
        model=prior_tool.contract.java(body)
        prior_tool.owner(model,role);prior_tool.protocol(compact,role)
        assert 'try(exchange){write(exchange);}' in compact
        for name,mutate in (('wrong-role',lambda r:r.update(package='dev.codex.schubert.nk.batch.monitoring')),('network-authority',lambda r:r['imports'].append('java.net.ServerSocket'))):
            changed_model=copy.deepcopy(model);mutate(changed_model)
            try: prior_tool.owner(changed_model,role)
            except AssertionError: role_negatives.append(role+':'+name)
            else: raise AssertionError('role mutation must reject')
        for name,changed_body in (('writer-closes-borrow',compact.replace('context.render(', 'context.close();context.render(',1)),('handle-drops-owner',compact.replace('try(exchange){write(exchange);}','write(exchange);',1))):
            assert changed_body!=compact
            try:
                prior_tool.protocol(changed_body,role)
                assert 'try(exchange){write(exchange);}' in changed_body
            except (AssertionError,ValueError): protocol_negatives.append(role+':'+name)
            else: raise AssertionError('owner protocol mutation must reject')
        manager=(snapshot/MANAGERS[role]).read_text()
        old=subprocess.check_output(['git','show',BEFORE+':'+MANAGERS[role]],cwd=host.ROOT,text=True)
        manager_rows[role]=manager_contract(manager,role,old)
        for name,changed_manager in (('lost-wildcard-target',manager.replace('Optional.<'+ROLES[role]+'MetricContext<?>>of','Optional.of',1)),('wrong-ready-authority',manager.replace('value, this::ready','value, healthy',1)),('double-exchange-owner',manager.replace('.write(exchange);','.handle(exchange);',1)),('manager-init',manager.replace('this.metricHandler =','context.initialize(); this.metricHandler =',1))):
            assert changed_manager!=manager
            try: manager_contract(changed_manager,role,old)
            except (AssertionError,ValueError): manager_negatives.append(role+':'+name)
            else: raise AssertionError('every manager ownership mutation rejects')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    fields={}
    for role,path in MAINS.items():
        compiled_class=snapshot/path.replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-handler-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s','-constants',str(compiled_class)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        fields[role]=dict(handler=handler_metadata(text,role),receipt=receipt)
        compiled_manager=snapshot/MANAGERS[role].replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-manager-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s',str(compiled_manager)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        assert 'private final java.util.Optional<dev.codex.schubert.nk.'+role+'.monitoring.'+ROLES[role]+'MetricHttpHandler> metricHandler;' in text
        assert text.count('static dev.codex.schubert.nk.'+role+'.bootstrap.'+ROLES[role]+'ManagementServer bind(')==4
        fields[role]['managerMetadataReceipt']=receipt
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1832 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1832,physicalAdded=[],physicalRemoved=[],physicalChanged={path:dict(before=old_physical[path],after=physical[path]) for path in sorted(CHANGED_CLASSES)},previousPhysicalUnchanged=1828,originalPhysicalUnchanged=1667,originalPhysicalChanged=sorted(original_changed),sourceRows=rows,sourceCount=223,currentTests=36,currentSuites=2,newTests=4,necessaryModifiedSourceRegression=32,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],managerPgReview=dict(scope=manager_rows,sourceNegativeChecks=manager_negatives,status='SOURCE_REVIEW_AND_COMPILE_ONLY_NOT_PT_EXEMPTED',dynamicPt='UNRUN_HOLD',coverage=None),handlerOwnerGuard=dict(roleNegatives=role_negatives,protocolNegatives=protocol_negatives,fields=fields),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,physical=1832,sourceOwners=223,changedMain=4,qualifiedHandlers=2,managerDynamicPt='UNRUN_HOLD',managerNegatives=len(manager_negatives),architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
