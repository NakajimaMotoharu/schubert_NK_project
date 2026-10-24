"""Current HTTP-boundary scoped proof; all old bytes retained, no product target initialized."""
import copy
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture, verify

host, architecture, steps = base.host, base.architecture, base.steps
SOURCE='db9c16e0360d7eeb76850feea93899d7a7f8753f'
BEFORE='f1b570e45f072b6001ad7e8e250ffbc5686c494a'
COMPILE=host.W/'pg8762-metric-http-fixed-six-compile-v1'
SLOT=host.W/'pg8768-metric-http-fixed-trace-v1'
OUT=host.BASE/'PG8768-metric-http-fixed-trace-v1'
ROLES={'api':'Api','web':'Web'}
MAINS={role:f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}MetricHttpHandler.java' for role,title in ROLES.items()}
ADDED=set(MAINS.values())|{path.replace('/main/','/test/').replace('.java','Test.java') for path in MAINS.values()}
CLASSES={role+':dev/codex/schubert/nk/'+role+'/monitoring/'+title+'MetricHttpHandler.class' for role,title in ROLES.items()}
NORMAL_SHA='1adea2b83c203ffaf1b7398f517ca9dede9e6642ea21e25ead12dac922e45912'
CURRENT_SHA='ec84d9d92e7448722a568f9a526fa692f6d49cec60cd4d4cfb35af7df8ef4146'

def owner(model,role):
    assert model['package']=='dev.codex.schubert.nk.'+role+'.monitoring' and model['type']==ROLES[role]+'MetricHttpHandler'
    assert {'com.sun.net.httpserver.HttpExchange','com.sun.net.httpserver.HttpHandler','java.util.function.BooleanSupplier','java.nio.charset.StandardCharsets'} <= set(model['imports'])
    forbidden=tuple('dev.codex.schubert.nk.'+other+'.' for other in ('api','web','batch','bootstrap') if other!=role)
    assert not any(value.startswith(forbidden+('java.net.','java.sql.','java.nio.file.','io.micrometer.')) for value in model['imports'])

def protocol(compact,role):
    assert 'implementsHttpHandler' in compact and 'try(exchange)' in compact
    assert 'if(!"GET".equals(exchange.getRequestMethod()))' in compact
    assert 'elseif(!PATH.equals(exchange.getRequestURI().getRawPath()))' in compact
    assert compact.count('context.render(ready.getAsBoolean())')==1
    assert compact.index('context.render(')<compact.index('exchange.sendResponseHeaders(')<compact.index('exchange.getResponseBody().write(bytes);')
    assert 'body.getBytes(StandardCharsets.UTF_8)' in compact
    assert 'exchange.sendResponseHeaders(status,bytes.length)' in compact
    assert 'exchange.getResponseHeaders().set("Cache-Control","no-store")' in compact
    assert 'context.initialize(' not in compact and 'context.close(' not in compact and 'new'+ROLES[role]+'MetricContext' not in compact
    assert 'catch(' not in compact and 'start(' not in compact

def metadata(text,role):
    qualified='dev.codex.schubert.nk.'+role+'.monitoring.'
    name=ROLES[role]+'MetricHttpHandler'
    lines=[line for line in text.splitlines() if line.strip()]
    assert lines[:2]==['Compiled from "'+name+'.java"','public final class '+qualified+name+' implements com.sun.net.httpserver.HttpHandler {']
    fields=[(line,lines[i+1]) for i,line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    assert len(fields)==5 and all(line.startswith('  private ') for line,_ in fields)
    names={re.search(r' ([A-Za-z_]\w*)(?: = .*)?;$',line).group(1) for line,_ in fields}
    assert names=={'PATH','METRIC_TYPE','JSON_TYPE','context','ready'}
    assert ('  private static final java.lang.String PATH = "/actuator/prometheus";','    descriptor: Ljava/lang/String;') in fields
    assert ('  private final '+qualified+ROLES[role]+'MetricContext<?> context;','    descriptor: L'+qualified.replace('.','/')+ROLES[role]+'MetricContext;') in fields
    public=[line.strip() for line in lines if line.startswith('  public ') and line.endswith(';')]
    assert public==['public '+qualified+name+'('+qualified+ROLES[role]+'MetricContext<?>, java.util.function.BooleanSupplier);','public void handle(com.sun.net.httpserver.HttpExchange) throws java.io.IOException;']
    return dict(fieldNames=sorted(names),publicApi=public)

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
        'normal':('PG8762-metric-http-fixed-six-compile-v1/manifest.json',NORMAL_SHA),
        'current':('PG8766-metric-http-fixed-post-v1/manifest.json',CURRENT_SHA),
        'priorNormal':('PG8740-metric-context-six-compile-v1/manifest.json','45fda0573fcd8709921be8374a6c77bbb598c7a51dab7b6faa9eb01c3fda3aff'),
        'priorTrace':('PG8746-metric-context-trace-v1/manifest.json','a18b07418877f5b366a3c84323210501ebdc11a5cb8f3d81309bdbe08614a86d'),
        'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
        'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in witnesses.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current,prior=proof['normal'],proof['current'],proof['priorNormal']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==32 and current['suites']==2 and len(current['executableClasses'])==2 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert prior['source']==proof['priorTrace']['source']==BEFORE
    before,after=prior['begin']['inputHashes'],normal['begin']['inputHashes']
    assert set(after)-set(before)==ADDED and not(set(before)-set(after)) and all(after[path]==digest for path,digest in before.items())
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    previous,physical=base.inventory(prior),base.inventory(normal)
    assert len(previous)==1830 and len(physical)==1832 and set(physical)-set(previous)==CLASSES and all(physical[path]==digest for path,digest in previous.items())
    original=proof['original']['allPhysicalMainSha256']
    assert len(original)==1669 and all(physical[path]==digest for path,digest in original.items())
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}==dict.fromkeys(ADDED,'A')
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==217 and not(set(old_rows)&ADDED)
    rows=[]
    for path in sorted(set(old_rows)|ADDED):
        digest=host.sha(snapshot/path)
        assert path in ADDED or old_rows[path]['sha256']==digest
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_BORROWED_HTTP_METRIC_BOUNDARY' if path in ADDED else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'))
    assert len(rows)==221
    models={};role_negatives=[];protocol_negatives=[]
    for role,path in MAINS.items():
        body=(snapshot/path).read_text();compact=''.join(body.split())
        model=contract.java(body);owner(model,role);protocol(compact,role);models[role]=model
        for name,mutate in (('wrong-role',lambda r:r.update(package='dev.codex.schubert.nk.batch.monitoring')),('bootstrap-owner',lambda r:r['imports'].append('dev.codex.schubert.nk.bootstrap.metric.Forbidden')),('network-authority',lambda r:r['imports'].append('java.net.ServerSocket'))):
            changed=copy.deepcopy(model);mutate(changed)
            try: owner(changed,role)
            except AssertionError: role_negatives.append(role+':'+name)
            else: raise AssertionError('every role mutation rejects')
        for name,changed in (('decoded-path',compact.replace('getRawPath()','getPath()',1)),('character-length',compact.replace('status,bytes.length','status,body.length()',1)),('context-close',compact.replace('try(exchange){','try(exchange){context.close();',1)),('missing-no-store',compact.replace('exchange.getResponseHeaders().set("Cache-Control","no-store");','',1))):
            assert changed!=compact
            try: protocol(changed,role)
            except (AssertionError,ValueError): protocol_negatives.append(role+':'+name)
            else: raise AssertionError('every protocol mutation rejects')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    fields={};field_negatives=[]
    for role,path in MAINS.items():
        compiled_class=snapshot/path.replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s','-constants',str(compiled_class)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        actual=metadata(text,role)
        for name,changed in (('public-context',text.replace('private final dev.codex.schubert.nk.'+role+'.monitoring.'+ROLES[role]+'MetricContext<?> context;','public final dev.codex.schubert.nk.'+role+'.monitoring.'+ROLES[role]+'MetricContext<?> context;',1)),('extra-lifecycle',text.replace('\n}','\n  public void close();\n}')),('path-change',text.replace('PATH = "/actuator/prometheus"','PATH = "/actuator/info"',1))):
            assert changed!=text
            try: metadata(changed,role)
            except AssertionError: field_negatives.append(role+':'+name)
            else: raise AssertionError('every field/API mutation rejects')
        fields[role]=dict(metadata=actual,receipt=receipt)
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1832 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation)
    OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1832,physicalAdded=sorted(CLASSES),physicalRemoved=[],physicalChanged={},previousPhysicalUnchanged=1830,originalPhysicalUnchanged=1669,sourceRows=rows,sourceCount=221,currentTests=32,currentSuites=2,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],ownerGuardBinding=dict(models=models,roleNegatives=role_negatives,protocolNegatives=protocol_negatives,fieldNegatives=field_negatives,roleFields=fields,allPriorSourcesUnchanged=True),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,physical=1832,sourceOwners=221,roleNegatives=len(role_negatives),protocolNegatives=len(protocol_negatives),fieldNegatives=len(field_negatives),architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
