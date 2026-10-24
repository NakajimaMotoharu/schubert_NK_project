"""Same-source map/consumer qualification + source-only native/pipeline wiring, never startup PT."""
from collections import Counter
import copy
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import pg8302_http_cdf_six_trace as base
import pg8938_web_service_metric_fixed_trace as previous
import pg8948_web_metric_pipeline_host as selected
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE=selected.SOURCE
BEFORE='fb5bde926943114412aa5a8ff3c3c06995efba4b'
MAIN=previous.MAIN
UNIT=previous.UNIT
NATIVE='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java'
HTTP='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java'
SLOT=host.W/'pg8952-web-metric-pipeline-trace-v1'
OUT=host.BASE/'PG8952-web-metric-pipeline-trace-v1'

def compact(text): return ''.join(text.split())

def protocol(text):
    previous.protocol(text)
    body=compact(text)
    assert 'publicMap<Class<?>,Object>withHttpObserver(Map<Class<?>,?>dependencies)' in body
    parts=['Objects.requireNonNull(dependencies,"HTTPmetricpipelinedependencies")','newHashMap<Class<?>,Object>()','for(varsupplied:dependencies.entrySet())','Objects.requireNonNull(supplied,"HTTPmetricdependencyentry")','Objects.requireNonNull(entry.getKey(),"HTTPmetricdependencytype")','Objects.requireNonNull(entry.getValue(),"HTTPmetricdependencyvalue")','if(!type.isInstance(value))','if(copied.putIfAbsent(type,value)!=null)','if(copied.containsKey(HttpMetricValve.class))','copied.put(HttpMetricValve.class,createHttpObserver());','returnMap.copyOf(copied);']
    positions=[body.index(token) for token in parts]
    assert positions==sorted(positions)

def caller(text,old):
    body=compact(text);prior=compact(old)
    new='metrics=WebServiceMetricBinding.prepareContext(config.value("nk.monitoring.mode"),()->HikariDataSource.class.cast(database).getHikariPoolMXBean(),()->HikariDataSource.class.cast(database).getHikariConfigMXBean(),failureSignal);varmetricOwner=Objects.requireNonNull(metrics);metricOwner.initialize();'
    legacy='metrics=WebDbPoolMetricBinding.prepareContext(config.value("nk.monitoring.mode"),()->HikariDataSource.class.cast(database).getHikariPoolMXBean(),()->HikariDataSource.class.cast(database).getHikariConfigMXBean());varmetricOwner=Objects.requireNonNull(metrics);metricOwner.initialize();'
    mapping='(core,sessions)->{vardependencies=assembly.dependencies(core,sessions);varbinding=metricOwner.bindings();returnbinding.isPresent()?binding.orElseThrow().withHttpObserver(dependencies):dependencies;}'
    marker='requireMappings(Objects.requireNonNull(http).mappedPaths());'
    assert body.count(new)==body.count(mapping)==1
    assert body.index(new)<body.index('varassembly=')<body.index('application.startOwnedWithCoreSessionDependencies(')
    reconstructed=body.replace(new,'',1).replace(mapping,'assembly::dependencies',1)
    reconstructed=reconstructed.replace(marker,marker+legacy,1)
    reconstructed=reconstructed.replace('importdev.codex.schubert.nk.web.monitoring.WebServiceMetricBinding;','importdev.codex.schubert.nk.web.monitoring.WebDbPoolMetricBinding;',1)
    # Google format sorts the replaced import, so compare the declaration set separately.
    def imports(value): return set(re.findall(r'import[^;]+;',value))
    assert imports(reconstructed)==imports(prior)
    reconstructed=re.sub(r'import[^;]+;','',reconstructed).replace('WebMetricContext<WebServiceMetricBinding>','WebMetricContext<WebDbPoolMetricBinding>',1)
    prior=re.sub(r'import[^;]+;','',prior)
    assert reconstructed==prior
    assert Counter(re.findall(r'"(?:\\.|[^"\\])*"',text))==Counter(re.findall(r'"(?:\\.|[^"\\])*"',old))

def pipeline(text,old):
    body=compact(text)
    pre='if(registeredDependencies.containsKey(HttpMetricValve.class)&&!registeredDependencies.containsKey(WebRequestLogProducer.class))thrownewIllegalArgumentException("HTTPmetricobserverrequiresrequesttrace");'
    observer='ObjectmetricObserver=registeredDependencies.get(HttpMetricValve.class);if(metricObserver!=null){context.getPipeline().addValve((HttpMetricValve)metricObserver);}'
    assert body.count(pre)==body.count(observer)==1
    assert body.index(pre)<body.index('varresult=newWebHttpServer(tomcatFactory);')
    assert body.index('newHttpRequestLoggingValve(')<body.index(observer)<body.index('newWebHttpAdmissionValve(')
    restored=body.replace(pre,'',1).replace(observer,'',1).replace('importdev.codex.schubert.nk.web.monitoring.HttpMetricValve;','',1)
    assert restored==compact(old)

def fields(text):
    added=[line.strip() for line in text.splitlines() if line.startswith('  public ') and ' withHttpObserver(' in line]
    assert len(added)==1 and added[0].startswith('public java.util.Map<java.lang.Class<?>, java.lang.Object> withHttpObserver(')
    retained=previous.fields('\n'.join(line for line in text.splitlines() if ' withHttpObserver(' not in line))
    retained['newPublicApi']=added
    return retained

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG8946-web-metric-pipeline-six-compile-v1/manifest.json',selected.COMPILE_SHA),
      'post':('PG8950-web-metric-pipeline-post-v1/manifest.json',host.sha(host.BASE/'PG8950-web-metric-pipeline-post-v1/manifest.json')),
      'priorNormal':('PG8932-web-service-metric-fixed-six-compile-v1/manifest.json','290375db61b4dbe62e728783e2d7c475b69478e65c7152f36da8edb3d552f49e'),
      'priorTrace':('PG8938-web-service-metric-fixed-trace-v1/manifest.json','2066440e1f6cb47643b83d6433da42e934e38301d538d7b5174f5ffd3d991b6c'),
      'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current=proof['normal'],proof['post']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==normal['testsExecuted']==0
    assert current['tests']==44 and current['suites']==2 and len(current['executableClasses'])==2
    assert current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert current['unclassified']==0 and not current['classifiedPmdContext'] and current['suppressionsAdded'] is False
    assert proof['priorNormal']['source']==proof['priorTrace']['source']==BEFORE
    snapshot=selected.COMPILE/'snapshot';hashes=normal['begin']['inputHashes']
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    before=base.inventory(proof['priorNormal']);physical=base.inventory(normal)
    changed={name:dict(beforeSha256=before[name],sha256=digest) for name,digest in physical.items() if before[name]!=digest}
    expected={'web:dev/codex/schubert/nk/web/'+name for name in ('monitoring/WebServiceMetricBinding.class','bootstrap/WebNativeRuntime.class','bootstrap/WebHttpServer.class')}
    assert len(physical)==len(before)==1835 and set(physical)==set(before) and set(changed)==expected
    original=proof['original']['allPhysicalMainSha256'];unchanged=sum(physical[name]==digest for name,digest in original.items())
    assert len(original)==1669 and unchanged==1664
    for name,digest in current['physicalClasses'].items(): assert physical['web:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT,NATIVE,HTTP}
    rows=copy.deepcopy(proof['priorTrace']['sourceRows']);indexed={row['path']:row for row in rows}
    assert len(rows)==len(indexed)==231 and delta-set(indexed)=={HTTP}
    rows.append(dict(path=HTTP));indexed={row['path']:row for row in rows}
    assert len(rows)==len(indexed)==232 and delta<=set(indexed)
    for path,row in indexed.items():
        assert host.sha(snapshot/path)==hashes[path]
        if path not in delta: assert row['sha256']==hashes[path]
        row.update(sha256=hashes[path],owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_CALLER_PG_NATIVE_UNRUN' if path in {NATIVE,HTTP} else 'CURRENT_MAP_SELECTED_PT' if path in delta else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION')
    old={path:subprocess.check_output(['git','show',BEFORE+':'+path],cwd=host.ROOT,text=True) for path in delta}
    text=(snapshot/MAIN).read_text();native=(snapshot/NATIVE).read_text();http=(snapshot/HTTP).read_text()
    protocol(text);caller(native,old[NATIVE]);pipeline(http,old[HTTP])
    begin=text.rfind('  /**',0,text.index('  public Map<Class<?>, Object> withHttpObserver('))
    restored=text[:begin].replace('import java.util.HashMap;\n','',1).replace('import java.util.Map;\n','',1).rstrip()+'\n}\n'
    assert restored==old[MAIN]
    unit=(snapshot/UNIT).read_text();begin=unit.index('  @Test\n  void webservice015')
    assert unit[:begin].rstrip()+'\n}\n'==old[UNIT]
    negatives=[]
    for name,bad,check in [('drop-type-check',text.replace('if (!type.isInstance(value))','if (false)',1),lambda value:protocol(value)),('overwrite-duplicate',text.replace('copied.putIfAbsent(type, value)','copied.put(type, value)',1),lambda value:protocol(value)),('mutable-map',text.replace('return Map.copyOf(copied);','return copied;',1),lambda value:protocol(value)),('drop-context-init',native.replace('metricOwner.initialize();','',1),lambda value:caller(value,old[NATIVE])),('drop-std-bypass',native.replace(': dependencies;',': binding.orElseThrow().withHttpObserver(dependencies);',1),lambda value:caller(value,old[NATIVE])),('remove-trace-precondition',http.replace('&& !registeredDependencies.containsKey(WebRequestLogProducer.class)','',1),lambda value:pipeline(value,old[HTTP])),('wrong-pipeline-type',http.replace('.addValve((HttpMetricValve) metricObserver);','.addValve((WebHttpAdmissionValve) metricObserver);',1),lambda value:pipeline(value,old[HTTP]))]:
        assert bad not in (text,native,http)
        try: check(bad)
        except (AssertionError,ValueError): negatives.append(name)
        else: raise AssertionError('each map/caller/pipeline mutation rejects')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    classfile=snapshot/MAIN.replace('/src/main/java/','/target/classes/').replace('.java','.class')
    receipt,metadata=steps.step('service-binding-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s',str(classfile)])
    assert receipt['actualExit']==0;declarations=fields(metadata)
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1835 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,physicalClasses=physical,allPhysicalClassCount=1835,physicalChanged=changed,previousPhysicalUnchanged=1832,originalPhysicalUnchanged=unchanged,sourceRows=rows,sourceCount=232,currentTests=44,currentSuites=2,newTests=8,necessaryModifiedSourceRegression=36,currentCounters=current['counters'],protocolNegatives=negatives,fields=declarations,fieldReceipt=receipt,oldServiceCoreAnd14TestBodiesUnchanged=True,callerAndHttpRestoredOldSourceProtocol=True,architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,callerDynamicPt='UNRUN_HOLD',callerCoverage=None,ptExecutionExempt=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1835,sourceOwners=232,protocolNegatives=len(negatives),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
