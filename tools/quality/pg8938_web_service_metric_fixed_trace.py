"""New Web service binding physical/source/borrowed ownership proof; no actual pipeline startup."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import pg8934_web_service_metric_fixed_host as selected
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE=selected.SOURCE
BEFORE='3359b14899beb17538b1408fe6ea63566f818a00'
MAIN='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebServiceMetricBinding.java'
UNIT=MAIN.replace('/main/','/test/').replace('.java','Test.java')
HTTP='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricHttpHandlerTest.java'
SLOT=host.W/'pg8938-web-service-metric-fixed-trace-v1'
OUT=host.BASE/'PG8938-web-service-metric-fixed-trace-v1'

def protocol(text):
    body=''.join(text.split())
    assert 'packagedev.codex.schubert.nk.web.monitoring;' in body
    assert 'privatefinalWebDbPoolMetricBindingdatabase;' in body and 'privatefinalHttpMetricRecorderhttp;' in body and 'privatefinalRunnableterminal;' in body
    assert 'database=newWebDbPoolMetricBinding(pool,config,registry,mode);http=newHttpMetricRecorder(registry,mode);' in body
    assert 'publicvoidrefresh(){database.refresh();}' in body and 'publicHttpMetricValvecreateHttpObserver(){returnnewHttpMetricValve(http,terminal);}' in body
    assert 'Objects.requireNonNull(terminal,"HTTPmetricterminalsignal");' in body
    assert 'returnnewWebMetricContext<WebServiceMetricBinding>(mode,registry->newWebServiceMetricBinding(Objects.requireNonNull(pool.get(),"borrowedpoolobservation"),Objects.requireNonNull(config.get(),"borrowedpoolconfigurationobservation"),registry,mode,terminal),WebServiceMetricBinding::refresh);' in body
    for denied in ('java.net.','java.sql.','javax.sql.','javax.management.','java.lang.reflect.','dev.codex.schubert.nk.api.','dev.codex.schubert.nk.batch.','dev.codex.schubert.nk.bootstrap.','getConnection(','getPassword(','getUsername(','softEvictConnections(','suspendPool(','resumePool(','.close(','.start(','.log(','catch('):
        assert denied not in body

def fields(text):
    declarations=[line.strip() for line in text.splitlines() if line.startswith('  ') and not line.startswith('    ')]
    fields=[line for line in declarations if line.endswith(';') and '(' not in line]
    prefix='dev.codex.schubert.nk.web.monitoring.'
    assert fields==['private final '+prefix+'WebDbPoolMetricBinding database;','private final '+prefix+'HttpMetricRecorder http;','private final java.lang.Runnable terminal;']
    public=[line for line in declarations if line.startswith('public ') and line.endswith(';')]
    assert len(public)==4 and any(' prepareContext(' in line for line in public)
    assert 'public void refresh();' in public and 'public '+prefix+'HttpMetricValve createHttpObserver();' in public
    assert 'implements java.lang.AutoCloseable' not in text and 'MeterRegistry registry();' not in text
    return dict(privateRetainedFields=fields,publicApi=public,resourceOwner=False)

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG8932-web-service-metric-fixed-six-compile-v1/manifest.json',selected.COMPILE_SHA),
      'post':('PG8936-web-service-metric-fixed-post-v1/manifest.json',host.sha(host.BASE/'PG8936-web-service-metric-fixed-post-v1/manifest.json')),
      'priorNormal':('PG8910-batch-full-text-static-fixed-six-compile-v1/manifest.json','bdc542236d6e176680afeaa1b02a181cb501117b961b48e0e5a5a7bc0a7543a8'),
      'priorTrace':('PG8916-batch-full-text-static-fixed-trace-v1/manifest.json','8f022a7a88069e620fa2e9a374339f9a2890a5865ec3d8f8bcc1e0f7c1961031'),
      'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current=proof['normal'],proof['post']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==normal['testsExecuted']==0
    assert current['tests']==36 and current['suites']==2 and len(current['executableClasses'])==2
    assert current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert current['unclassified']==0 and not current['classifiedPmdContext'] and current['suppressionsAdded'] is False
    assert proof['priorNormal']['source']==proof['priorTrace']['source']==BEFORE
    snapshot=selected.COMPILE/'snapshot';hashes=normal['begin']['inputHashes']
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    previous=base.inventory(proof['priorNormal']);physical=base.inventory(normal)
    added=set(physical)-set(previous)
    assert len(physical)==1835 and len(previous)==1834 and added=={'web:dev/codex/schubert/nk/web/monitoring/WebServiceMetricBinding.class'}
    assert all(physical[name]==digest for name,digest in previous.items())
    original=proof['original']['allPhysicalMainSha256']
    unchanged=sum(physical[name]==digest for name,digest in original.items())
    assert len(original)==1669 and unchanged==1665
    for name,digest in current['physicalClasses'].items(): assert physical['web:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT,HTTP}
    rows=copy.deepcopy(proof['priorTrace']['sourceRows']);indexed={row['path']:row for row in rows}
    assert len(rows)==len(indexed)==229 and delta-set(indexed)=={MAIN,UNIT}
    rows.extend(dict(path=path) for path in sorted(delta-set(indexed)))
    indexed={row['path']:row for row in rows};assert len(rows)==len(indexed)==231 and delta<=set(indexed)
    for path,row in indexed.items():
        assert host.sha(snapshot/path)==hashes[path]
        if path not in delta: assert row['sha256']==hashes[path]
        row.update(sha256=hashes[path],owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_WEB_SERVICE_SELECTED_PT' if path in delta else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION')
    text=(snapshot/MAIN).read_text();protocol(text)
    unit=(snapshot/HTTP).read_text();old_unit=subprocess.check_output(['git','show',BEFORE+':'+HTTP],cwd=host.ROOT,text=True)
    begin=unit.index('  @Test\n  void webmhttp022');end=unit.index('  private static WebMetricContext<String> standard()')
    assert unit[:begin]+unit[end:]==old_unit
    negatives=[]
    for name,bad in [('foreign-role',text.replace('package dev.codex.schubert.nk.web.monitoring;','package dev.codex.schubert.nk.api.monitoring;',1)),('weakened-retention',text.replace('private final HttpMetricRecorder http;','private HttpMetricRecorder http;',1)),('http-replay-on-refresh',text.replace('database.refresh();','database.refresh();http.log(null,null,0);',1)),('implicit-close',text.replace('return new HttpMetricValve(http, terminal);','http.close();return new HttpMetricValve(http, terminal);',1)),('dropped-terminal-boundary',text.replace('Objects.requireNonNull(terminal, "HTTP metric terminal signal");','',2))]:
        assert bad!=text
        try: protocol(bad)
        except AssertionError: negatives.append(name)
        else: raise AssertionError('every service owner/protocol mutation rejects')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    classfile=snapshot/MAIN.replace('/src/main/java/','/target/classes/').replace('.java','.class')
    receipt,metadata=steps.step('service-binding-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s',str(classfile)])
    assert receipt['actualExit']==0
    declarations=fields(metadata);field_negatives=[]
    for name,bad in [('public-field',metadata.replace('private final dev.codex.schubert.nk.web.monitoring.HttpMetricRecorder http;','public final dev.codex.schubert.nk.web.monitoring.HttpMetricRecorder http;',1)),('mutable-field',metadata.replace('private final dev.codex.schubert.nk.web.monitoring.HttpMetricRecorder http;','private dev.codex.schubert.nk.web.monitoring.HttpMetricRecorder http;',1))]:
        assert bad!=metadata
        try: fields(bad)
        except AssertionError: field_negatives.append(name)
        else: raise AssertionError('every field mutation rejects')
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1835 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,physicalClasses=physical,allPhysicalClassCount=1835,physicalAdded=sorted(added),previousPhysicalUnchanged=1834,originalPhysicalUnchanged=unchanged,sourceRows=rows,sourceCount=231,currentTests=36,currentSuites=2,newTests=15,necessaryModifiedSourceRegression=21,currentCounters=current['counters'],protocolNegatives=negatives,fields=declarations,fieldReceipt=receipt,fieldNegatives=field_negatives,old21HttpTestBodiesUnchanged=True,architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1835,sourceOwners=231,protocolNegatives=len(negatives),fieldNegatives=len(field_negatives),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
