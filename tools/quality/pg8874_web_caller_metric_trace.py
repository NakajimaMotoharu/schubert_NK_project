"""All physical bytes/current source owners + API caller PG source protocol; not native PT."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import pg8870_web_caller_metric_host as selected
from host_tool_invocation import capture, verify

host, architecture, steps = base.host, base.architecture, base.steps
SOURCE=selected.SOURCE
BEFORE='0f065c63fe1667e014fa4b985579d4146c3d91c5'
SLOT=host.W/'pg8874-web-caller-metric-trace-v1'
OUT=host.BASE/'PG8874-web-caller-metric-trace-v1'
CALLER='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java'
BINDING='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricBinding.java'
UNITS={name:'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/'+name+'.java' for name in selected.COUNTS}

def compact(text):
    return ''.join(text.split())

def caller_guard(text, old):
    body, prior=compact(text),compact(old)
    begin='metrics=WebDbPoolMetricBinding.prepareContext(config.value("nk.monitoring.mode"),()->HikariDataSource.class.cast(database).getHikariPoolMXBean(),()->HikariDataSource.class.cast(database).getHikariConfigMXBean());varmetricOwner=Objects.requireNonNull(metrics);metricOwner.initialize();'
    field='private@NullableWebMetricContext<WebDbPoolMetricBinding>metrics;'
    phase='left->{varvalue=metrics;if(value!=null)value.close();},'
    assert body.count(begin)==body.count(field)==body.count(phase)==1
    assert body.index('varvalue=management;')<body.index('varvalue=metrics;')<body.index('varvalue=assets;')
    assert 'WebManagementServer.bind(information,this::healthy,ports.applyAsInt(config,"nk.web.management.port"),com.sun.net.httpserver.HttpServer::create,metricOwner)' in body
    reconstructed=body.replace(begin,'',1).replace(field,'',1).replace(phase,'',1)
    for name in ('com.zaxxer.hikari.HikariDataSource','dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricBinding','dev.codex.schubert.nk.web.monitoring.WebMetricContext'):
        reconstructed=reconstructed.replace('import'+name+';','',1)
    reconstructed=reconstructed.replace('com.sun.net.httpserver.HttpServer::create,metricOwner)','com.sun.net.httpserver.HttpServer::create)',1)
    assert reconstructed==prior

def factory_guard(text):
    body=compact(text)
    assert 'publicstaticWebMetricContext<WebDbPoolMetricBinding>prepareContext(' in body
    assert 'returnnewWebMetricContext<WebDbPoolMetricBinding>(mode,registry->newWebDbPoolMetricBinding(Objects.requireNonNull(pool.get(),"borrowedpoolobservation"),Objects.requireNonNull(config.get(),"borrowedpoolconfigurationobservation"),registry,mode),WebDbPoolMetricBinding::refresh);' in body
    assert 'Objects.requireNonNull(pool,"borrowedpoolsupplier");' in body
    assert 'Objects.requireNonNull(config,"borrowedpoolconfigurationsupplier");' in body
    assert body.count('pool.get()')==body.count('config.get()')==1
    assert 'privatefinalHikariPoolMXBeanpool;' in body and 'privatefinalHikariConfigMXBeanconfig;' in body
    for denied in ('getConnection(', 'softEvictConnections(', 'suspendPool(', 'resumePool(', 'getPassword(', 'getUsername(', '.close(', 'newHikariDataSource(', 'java.net.', 'javax.sql.'):
        assert denied not in body

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG8868-web-caller-metric-six-compile-v1/manifest.json',selected.COMPILE_SHA),
      'post':('PG8872-web-caller-metric-post-v1/manifest.json','177a2494065726f470a17053fed0cc47e6d06ae1d897bc3ea1f9a1d285b37aa0'),
      'priorNormal':('PG8854-api-caller-metric-six-compile-v1/manifest.json','7aa656748674bd692a4d6132bff0c60e3470f70435f556b750eb67fc64aa0ba1'),
      'priorTrace':('PG8862-api-caller-metric-fixed-trace-v1/manifest.json','0ec61b72ac1bbdf7935050b8e15aee69de5f13c95112df58ee87af79734f6e39'),
      'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current=proof['normal'],proof['post']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==36 and current['suites']==2 and len(current['executableClasses'])==3
    assert current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert current['unclassified']==0 and len(current['classifiedPmdContext'])==3 and current['suppressionsAdded'] is False
    assert proof['priorNormal']['source']==proof['priorTrace']['source']==BEFORE
    snapshot=selected.COMPILE/'snapshot'
    hashes=normal['begin']['inputHashes']
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    prior=base.inventory(proof['priorNormal']);physical=base.inventory(normal)
    expected={'web:dev/codex/schubert/nk/web/'+kind for kind in ('monitoring/WebDbPoolMetricBinding.class','bootstrap/WebNativeRuntime.class')}
    changed={name:dict(beforeSha256=prior[name],sha256=digest) for name,digest in physical.items() if prior[name]!=digest}
    assert len(physical)==len(prior)==1834 and set(physical)==set(prior) and set(changed)==expected
    original=proof['original']['allPhysicalMainSha256']
    unchanged=sum(physical[name]==digest for name,digest in original.items())
    assert len(original)==1669 and unchanged==1665
    for name,digest in current['physicalClasses'].items():
        assert physical['web:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={CALLER,BINDING,*UNITS.values()}
    rows=copy.deepcopy(proof['priorTrace']['sourceRows'])
    assert len(rows)==228 and len({row['path'] for row in rows})==228
    indexed={row['path']:row for row in rows}
    assert delta-set(indexed)=={CALLER}
    rows.append(dict(path=CALLER))
    indexed={row['path']:row for row in rows}
    assert len(rows)==len(indexed)==229 and delta<=set(indexed)
    owner_negatives=[]
    for name,bad in [('missing-caller',rows[:-1]),('duplicate-caller',rows+[dict(path=CALLER)])]:
        paths=[row['path'] for row in bad]
        if len(paths)!=len(set(paths)) or len(paths)!=229 or not delta<=set(paths): owner_negatives.append(name)
        else: raise AssertionError('owner counterexample must reject')
    for path,row in indexed.items():
        assert host.sha(snapshot/path)==hashes[path]
        if path not in delta: assert row['sha256']==hashes[path]
        row.update(sha256=hashes[path],owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_CALLER_PG_NATIVE_UNRUN' if path==CALLER else 'CURRENT_FACTORY_SELECTED_PT' if path in delta else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION')
    old_caller=subprocess.check_output(['git','show',BEFORE+':'+CALLER],cwd=host.ROOT,text=True)
    caller=(snapshot/CALLER).read_text();factory=(snapshot/BINDING).read_text()
    caller_guard(caller,old_caller);factory_guard(factory)
    negatives=[]
    for name,changed_text in (
      ('dropped-init',caller.replace('metricOwner.initialize();','',1)),
      ('dropped-phase',caller.replace('var value = metrics;','var value = assets;',1)),
      ('wrong-mode',caller.replace('"nk.monitoring.mode"','"wrong.mode"',1)),
      ('changed-admission',caller.replace('admission.admit();','',1))):
        assert changed_text!=caller
        try: caller_guard(changed_text,old_caller)
        except (AssertionError,ValueError): negatives.append(name)
        else: raise AssertionError('caller mutation must reject')
    for name,changed_text in (
      ('supplier-order',factory.replace('pool.get()','config.get()',1)),
      ('dropped-null-boundary',factory.replace('Objects.requireNonNull(pool, "borrowed pool supplier");','',1)),
      ('connection-acquire',factory.replace('collector.collect(pool, config);','pool.getConnection();collector.collect(pool, config);',1))):
        assert changed_text!=factory
        try: factory_guard(changed_text)
        except AssertionError: negatives.append(name)
        else: raise AssertionError('factory mutation must reject')
    # Preserve all old test declarations/bodies; only the six specified methods may be added.
    for name,path in UNITS.items():
        before=subprocess.check_output(['git','show',BEFORE+':'+path],cwd=host.ROOT,text=True)
        after=(snapshot/path).read_text()
        prefix='webpoolb' if name=='WebDbPoolMetricBindingTest' else 'webmhttp'
        number=11 if prefix=='webpoolb' else 21
        begin=after.index('  @Test\n  void '+prefix+str(number).zfill(3))
        end=after.index('  private static void await(') if prefix=='webpoolb' else after.index('  private static WebMetricContext<String> standard()')
        assert after[:begin]+after[end:]==before
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1834 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,physicalClasses=physical,allPhysicalClassCount=1834,physicalChanged=changed,previousPhysicalUnchanged=1832,originalPhysicalUnchanged=unchanged,sourceRows=rows,sourceCount=229,currentTests=36,currentSuites=2,newTests=6,necessaryModifiedSourceRegression=30,currentCounters=current['counters'],callerSourceProtocolNegatives=negatives,oldTestBodiesUnchanged=True,ownerNegatives=owner_negatives,architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,callerDynamicPt='UNRUN_HOLD',callerCoverage=None,ptExecutionExempt=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1834,sourceOwners=229,sourceProtocolNegatives=len(negatives),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
