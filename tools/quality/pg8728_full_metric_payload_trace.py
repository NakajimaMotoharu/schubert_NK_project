"""Full overload source/old-body byte/public constants/all-six trace, no service operations."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='3613b2742c8bcda85a2ec889d023307fadf1875c'
BEFORE='4c97764a913a09fd39d9881eb6e112e66c1547e3'
COMPILE=host.W/'pg8722-full-metric-payload-six-compile-v1'
SLOT=host.W/'pg8728-full-metric-payload-trace-v1'
OUT=host.BASE/'PG8728-full-metric-payload-trace-v1'
CURRENT_SHA='c26ae391c21885d64e19fa3033c05bc6e577b43f3c53aee052a00e8f755b67de'
ROLES={'api':'Api','web':'Web'}
MAINS={role:f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}CustomMetricPayload.java' for role,title in ROLES.items()}
CHANGED=set(MAINS.values())|{path.replace('/main/','/test/').replace('.java','Test.java') for path in MAINS.values()}
CLASSES={role+':dev/codex/schubert/nk/'+role+'/monitoring/'+title+'CustomMetricPayload.class' for role,title in ROLES.items()}

def owner(model,role):
    assert model['package']=='dev.codex.schubert.nk.'+role+'.monitoring' and model['type']==ROLES[role]+'CustomMetricPayload'
    assert {'io.micrometer.core.instrument.MeterRegistry','java.util.function.Supplier'}<=set(model['imports'])
    forbidden=tuple('dev.codex.schubert.nk.'+other+'.' for other in ('api','web','batch','bootstrap') if other!=role)
    assert not any(name.startswith(forbidden+('java.net.','java.sql.')) for name in model['imports'])

def prefix(role):
    return '# TYPE schubert_nk_'+role+'_ready gauge\nschubert_nk_'+role+'_ready '

def metadata(text,role):
    name=ROLES[role]+'CustomMetricPayload'
    qualified='dev.codex.schubert.nk.'+role+'.monitoring.'
    lines=[line for line in text.splitlines() if line.strip()]
    assert lines[:2]==['Compiled from "'+name+'.java"','public final class '+qualified+name+' {']
    fields=[(line,lines[i+1]) for i,line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    assert fields==[('  private static final java.lang.String STANDARD_MODE = "STANDARD";','    descriptor: Ljava/lang/String;'),('  private static final java.lang.String READY_PREFIX = '+json.dumps(prefix(role))+';','    descriptor: Ljava/lang/String;')]
    public=[line.strip() for line in lines if line.startswith('  public ') and line.endswith(';')]
    assert public==['public '+qualified+name+'();','public java.lang.String render(boolean, java.lang.String, java.util.function.Supplier<? extends io.micrometer.core.instrument.MeterRegistry>, '+qualified+ROLES[role]+'StandardMetricSource);','public java.lang.String render(boolean, java.lang.String, java.util.function.Supplier<? extends io.micrometer.core.instrument.MeterRegistry>);']
    return dict(fields=fields,publicApi=public,instanceFieldCount=0)

if __name__=='__main__':
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
        'normal':('PG8722-full-metric-payload-six-compile-v1/manifest.json','2cb763db0522c0bcc083c86585505d8dbec51e19700b7019c55548ca03a4c63e'),
        'current':('PG8726-full-metric-payload-post-v1/manifest.json',CURRENT_SHA),
        'originalRun':('PG8724-full-metric-payload-host-v1/manifest.json','8e87d9d6de971f04d11c47f1c9349d4359fe0c021b76068116dd307e31c81cd9'),
        'priorNormal':('PG8710-web-batch-standard-source-fixed-six-compile-v1/manifest.json','d4e08af5550e1da687757e2279f3f4faca6192b50a4de3d7a3efc6dd1d70d374'),
        'priorTrace':('PG8716-web-batch-standard-source-trace-v1/manifest.json','9dae72795fb1af89d3cc7bba2ca3cd24d2f7a66518b7b5b456ae94ea534f4c0e'),
        'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
        'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in witnesses.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current,prior=proof['normal'],proof['current'],proof['priorNormal']
    assert normal['source']==current['source']==proof['originalRun']['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==proof['originalRun']['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==50 and current['suites']==2 and len(current['executableClasses'])==2 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert prior['source']==proof['priorTrace']['source']==BEFORE
    before,after=prior['begin']['inputHashes'],normal['begin']['inputHashes']
    assert set(before)==set(after) and {path for path,digest in before.items() if after[path]!=digest}==CHANGED
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    previous,physical=base.inventory(prior),base.inventory(normal)
    assert len(previous)==len(physical)==1828 and set(previous)==set(physical) and {path for path,digest in previous.items() if physical[path]!=digest}==CLASSES
    original=proof['original']['allPhysicalMainSha256']
    assert len(original)==1669 and all(physical[path]==digest for path,digest in original.items())
    for path,digest in current['physicalClasses'].items():
        role=next(role for role in ROLES if path.startswith('dev/codex/schubert/nk/'+role+'/'))
        assert physical[role+':'+path]==digest
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}==dict.fromkeys(CHANGED,'M')
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==213 and CHANGED<=set(old_rows)
    rows=[]
    for path in sorted(old_rows):
        digest=host.sha(snapshot/path)
        assert path in CHANGED or old_rows[path]['sha256']==digest
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_FULL_OVERLOAD_SOURCE' if path in CHANGED else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'))
    classification={};models={};role_negatives=[];legacy=[]
    for role,path in MAINS.items():
        body=(snapshot/path).read_text()
        old_body=subprocess.check_output(['git','show',BEFORE+':'+path],cwd=host.ROOT,text=True)
        anchor='  /** Supplied ready state is not recomputed.'
        assert body[body.index(anchor):body.rfind('\n}')]==old_body[old_body.index(anchor):old_body.rfind('\n}')]
        unit=path.replace('/main/','/test/').replace('.java','Test.java')
        old_unit=subprocess.check_output(['git','show',BEFORE+':'+unit],cwd=host.ROOT,text=True)
        new_unit=(snapshot/unit).read_text()
        assert new_unit[:new_unit.index('  private static final String FULL_STANDARD')].rstrip()==old_unit[:old_unit.rfind('\n}')].rstrip()
        model=contract.java(body);owner(model,role);models[role]=model
        compact=''.join(body.split())
        assert compact.count('source.get()')==1 and compact.count('standard.scrape(mode)')==1 and '.close(' not in compact and '.bind(' not in compact
        assert 'if(STANDARD_MODE.equals(mode))returnrender(ready,mode,source);' in compact
        assert 'Objects.requireNonNull(standard.scrape(mode),"standardmetrictext")' in compact
        assert json.dumps(prefix(role)) in body
        server=f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{ROLES[role]}ManagementServer.java'
        assert before[server]==after[server] and json.dumps(prefix(role)) in (snapshot/server).read_text()
        legacy.append(dict(path=server,sha256=after[server],prefix=prefix(role),handlerChanged=False))
        actual=[row for row in proof['originalRun']['cases'] if row['classname']=='dev.codex.schubert.nk.'+role+'.monitoring.'+ROLES[role]+'CustomMetricPayloadTest']
        new=[row['name'] for row in actual if row['name'].startswith(role+'full')]
        compatibility=[row['name'] for row in actual if row['name'].startswith(role+'pay')]
        assert len(actual)==25 and len(new)==12 and len(compatibility)==13
        classification[role]=dict(newCases=new,necessaryChangedClassCompatibility=compatibility,newCount=12,compatibilityCount=13)
        for name,mutate in (('wrong-role',lambda r:r.update(package='dev.codex.schubert.nk.batch.monitoring')),('bootstrap-owner',lambda r:r['imports'].append('dev.codex.schubert.nk.bootstrap.metric.Forbidden')),('network-authority',lambda r:r['imports'].append('java.net.ServerSocket'))):
            changed=copy.deepcopy(model);mutate(changed)
            try:owner(changed,role)
            except AssertionError:role_negatives.append(role+':'+name)
            else:raise AssertionError('every role mutation rejects')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    field_rows={};field_negatives=[]
    for role,path in MAINS.items():
        compiled_class=snapshot/path.replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s','-constants',str(compiled_class)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        actual=metadata(text,role)
        ctor='  public dev.codex.schubert.nk.'+role+'.monitoring.'+ROLES[role]+'CustomMetricPayload();'
        for name,changed in (('retained-owner',text.replace(ctor,'  private final java.lang.Object owner;\n    descriptor: Ljava/lang/Object;\n'+ctor)),('wrong-standard-mode',text.replace('STANDARD_MODE = "STANDARD"','STANDARD_MODE = "DEBUG"')),('foreign-ready-prefix',text.replace('schubert_nk_'+role+'_ready','schubert_nk_batch_ready')),('public-resource-getter',text.replace('\n}','\n  public io.micrometer.core.instrument.MeterRegistry getRegistry();\n}')),('wrong-descriptor',text.replace('descriptor: Ljava/lang/String;','descriptor: Ljava/lang/Object;',1))):
            try:metadata(changed,role)
            except AssertionError:field_negatives.append(role+':'+name)
            else:raise AssertionError('every field/API mutation rejects')
        field_rows[role]=dict(metadata=actual,receipt=receipt)
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1828 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation)
    OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1828,physicalAdded=[],physicalRemoved=[],physicalChanged={path:dict(before=previous[path],after=physical[path]) for path in sorted(CLASSES)},previousPhysicalUnchanged=1826,originalPhysicalUnchanged=1669,sourceRows=rows,sourceCount=213,currentTests=50,currentSuites=2,newTests=24,necessaryCompatibilityTests=26,testCaseClassification=classification,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],legacyThreeArgumentBodyUnchanged=True,prior26TestBodyUnchanged=True,legacyEndpointUnchanged=legacy,ownerGuardBinding=dict(models=models,roleNegatives=role_negatives,fieldNegatives=field_negatives,roleFields=field_rows,bootstrapSourcesUnchanged=34),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,physical=1828,sourceOwners=213,newTests=24,compatibilityTests=26,roleNegatives=len(role_negatives),fieldNegatives=len(field_negatives),architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))
