"""Typed borrowed pool60/six executable scope and all1834 physical/owner metadata; no actual DB."""
import copy
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import pg8826_metric_refresh_fixed_trace as previous_tool
from host_tool_invocation import capture,verify

host,architecture,steps=previous_tool.host,previous_tool.architecture,previous_tool.steps
SOURCE='1e4f4049881c158760d285ce798dd3c4b6d0abbd'
BEFORE='32041eafe19116bba7b90431f522371f0bcd8d53'
COMPILE=host.W/'pg8842-typed-pool-binding-fixed-six-compile-v1'
SLOT=host.W/'pg8848-typed-pool-binding-fixed-trace-v1'
OUT=host.BASE/'PG8848-typed-pool-binding-fixed-trace-v1'
NORMAL_SHA='067a5c46b02c9b99119cfc8837e83fa652ab7c8d3fa30e98eb67da3c4ac35e4d'
CURRENT_SHA='365f0a72fdf78122ca14db3ce8808a9a2a421dbc7ac35f191a2ddbcc3926dc1d'
ROLES={'api':'Api','web':'Web'}
MAINS={role:f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}DbPoolMetricBinding.java' for role,title in ROLES.items()}
ADDED=set(MAINS.values())|{path.replace('/main/','/test/').replace('.java','Test.java') for path in MAINS.values()}
HTTP_UNITS={role:f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{title}MetricHttpHandlerTest.java' for role,title in ROLES.items()}
CLASSES={role+':dev/codex/schubert/nk/'+role+'/monitoring/'+title+'DbPoolMetricBinding.class' for role,title in ROLES.items()}
MANAGER_CLASSES=previous_tool.MANAGER_CLASSES

def owner(model,role):
    title=ROLES[role]
    assert model['package']==f'dev.codex.schubert.nk.{role}.monitoring' and model['type']==title+'DbPoolMetricBinding'
    assert {'com.zaxxer.hikari.HikariPoolMXBean','com.zaxxer.hikari.HikariConfigMXBean','io.micrometer.core.instrument.MeterRegistry'}<=set(model['imports'])
    forbidden=tuple('dev.codex.schubert.nk.'+other+'.' for other in ('api','web','batch','bootstrap') if other!=role)
    assert not any(name.startswith(forbidden+('java.sql.','javax.sql.','java.net.','java.nio.file.','javax.management.','java.lang.reflect.')) for name in model['imports'])

def protocol(compact,role):
    prefix='' if role=='api' else 'Web'
    assert 'privatefinalHikariPoolMXBeanpool;' in compact and 'privatefinalHikariConfigMXBeanconfig;' in compact
    assert 'privatefinal'+prefix+'DbPoolMetricCollectorcollector;' in compact
    assert compact.count('new'+prefix+'DbPoolMetricCollector(')==1 and compact.count('new'+prefix+'DbPoolMetricObservation()')==1
    assert 'publicvoidrefresh(){collector.collect(pool,config);}' in compact
    assert 'publicOptional<Counts>snapshot(){returncollector.snapshot();}' in compact
    assert compact.index('this.pool=Objects.requireNonNull(')<compact.index('this.collector=new')
    assert compact.index('this.config=Objects.requireNonNull(')<compact.index('this.collector=new')
    for token in ('getConnection(','softEvictConnections(','suspendPool(','resumePool(','getPassword(','getUsername(','getMBeanServer(','close(','catch('):
        assert token not in compact

def metadata(text,role):
    q='dev.codex.schubert.nk.'+role+'.monitoring.'
    name=ROLES[role]+'DbPoolMetricBinding'
    prefix='' if role=='api' else 'Web'
    lines=[line for line in text.splitlines() if line.strip()]
    assert lines[:2]==['Compiled from "'+name+'.java"','public final class '+q+name+' {']
    fields=[(line,lines[i+1]) for i,line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    assert fields==[('  private final com.zaxxer.hikari.HikariPoolMXBean pool;','    descriptor: Lcom/zaxxer/hikari/HikariPoolMXBean;'),('  private final com.zaxxer.hikari.HikariConfigMXBean config;','    descriptor: Lcom/zaxxer/hikari/HikariConfigMXBean;'),('  private final '+q+prefix+'DbPoolMetricCollector collector;','    descriptor: L'+q.replace('.','/')+prefix+'DbPoolMetricCollector;')]
    public=[line.strip() for line in lines if line.startswith('  public ') and line.endswith(';')]
    assert len(public)==3 and public[:2]==['public '+q+name+'(com.zaxxer.hikari.HikariPoolMXBean, com.zaxxer.hikari.HikariConfigMXBean, io.micrometer.core.instrument.MeterRegistry, java.lang.String);','public void refresh();']
    expected=r'public java\.util\.Optional<'+re.escape(q+prefix+'DbPoolMetricRecorder')+r'(?:\$|\.)Counts> snapshot\(\);'
    assert re.fullmatch(expected,public[2])
    return dict(fields=fields,publicApi=public,autoCloseable=False)

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
      'normal':('PG8842-typed-pool-binding-fixed-six-compile-v1/manifest.json',NORMAL_SHA),
      'current':('PG8846-typed-pool-binding-fixed-post-v1/manifest.json',CURRENT_SHA),
      'rationale':('PG8845-typed-pool-binding-context-v1/manifest.json','cf3d5cf4bbf752478679b6d41e6c942b59f69474924a889858930582650229f3'),
      'priorNormal':('PG8820-metric-refresh-fixed-six-compile-v1/manifest.json','8107b7e202b684ba02a3fedda816ef40f3a4dcb1fbe7dd7fb785508b6d4c3d54'),
      'priorTrace':('PG8826-metric-refresh-fixed-trace-v1/manifest.json','dbab6b7a10276bdd42a3a158fa92124b9a6c37908300116c20cc1937421e1b99'),
      'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in witnesses.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current,prior=proof['normal'],proof['current'],proof['priorNormal']
    assert normal['source']==current['source']==proof['rationale']['source']==SOURCE
    assert normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==proof['rationale']['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==60 and current['suites']==4 and len(current['executableClasses'])==6 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert len(current['classifiedPmdContext'])==6 and current['unclassified']==0 and current['suppressionsAdded'] is False
    assert prior['source']==proof['priorTrace']['source']==BEFORE
    before,after=prior['begin']['inputHashes'],normal['begin']['inputHashes']
    assert set(after)-set(before)==ADDED and not(set(before)-set(after))
    assert {path for path in before if before[path]!=after[path]}==set(HTTP_UNITS.values())
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    previous,physical=previous_tool.old_context.base.inventory(prior),previous_tool.old_context.base.inventory(normal)
    assert len(previous)==1832 and len(physical)==1834 and set(physical)-set(previous)==CLASSES and all(physical[path]==digest for path,digest in previous.items())
    original=proof['original']['allPhysicalMainSha256']
    assert len(original)==1669 and {path for path,digest in original.items() if physical[path]!=digest}==MANAGER_CLASSES
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}=={**dict.fromkeys(ADDED,'A'),**dict.fromkeys(HTTP_UNITS.values(),'M')}
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==223 and not(set(old_rows)&ADDED)
    rows=[]
    for path in sorted(set(old_rows)|ADDED):
        digest=host.sha(snapshot/path)
        assert path in ADDED|set(HTTP_UNITS.values()) or old_rows[path]['sha256']==digest
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_BORROWED_TYPED_POOL_BINDING' if path in ADDED else 'CURRENT_HTTP_CONSUMER_TEST' if path in HTTP_UNITS.values() else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'))
    assert len(rows)==227
    role_negatives=[];protocol_negatives=[];models={};preserved_tests={}
    for role,path in MAINS.items():
        body=(snapshot/path).read_text();compact=''.join(body.split())
        model=previous_tool.old_context.contract.java(body);owner(model,role);protocol(compact,role);models[role]=model
        for name,mutate in (('wrong-role',lambda row:row.update(package='dev.codex.schubert.nk.batch.monitoring')),('connection-authority',lambda row:row['imports'].append('javax.sql.DataSource')),('management-authority',lambda row:row['imports'].append('javax.management.MBeanServer'))):
            changed=copy.deepcopy(model);mutate(changed)
            try:owner(changed,role)
            except AssertionError:role_negatives.append(role+':'+name)
            else:raise AssertionError('every role mutation rejects')
        prefix='' if role=='api' else 'Web'
        for name,changed in (('dropped-retained-collector',compact.replace('privatefinal'+prefix+'DbPoolMetricCollectorcollector;','private'+prefix+'DbPoolMetricCollectorcollector;',1)),('control',compact.replace('collector.collect(pool,config);','pool.softEvictConnections();collector.collect(pool,config);',1)),('implicit-close',compact.replace('returncollector.snapshot();','collector.close();returncollector.snapshot();',1))):
            assert changed!=compact
            try:protocol(changed,role)
            except (AssertionError,ValueError):protocol_negatives.append(role+':'+name)
            else:raise AssertionError('every typed-owner mutation rejects')
        http=(snapshot/HTTP_UNITS[role]).read_text()
        old=subprocess.check_output(['git','show',BEFORE+':'+HTTP_UNITS[role]],cwd=host.ROOT,text=True)
        begin=http.index('  @Test\n  void '+role+'mhttp020')
        end=http.index('  private static '+ROLES[role]+'MetricContext<String> standard()')
        assert http[:begin]+http[end:]==old
        preserved_tests[role]=dict(oldHttp19BodiesUnchanged=True)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    fields={};field_negatives=[]
    for role,path in MAINS.items():
        file=snapshot/path.replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-binding-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s',str(file)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        fields[role]=dict(metadata=metadata(text,role),receipt=receipt)
        for name,changed in (('public-pool-field',text.replace('private final com.zaxxer.hikari.HikariPoolMXBean pool;','public final com.zaxxer.hikari.HikariPoolMXBean pool;',1)),('resource-owner',text.replace('DbPoolMetricBinding {','DbPoolMetricBinding implements java.lang.AutoCloseable {',1)),('exposed-config',text.replace('\n}','\n  public com.zaxxer.hikari.HikariConfigMXBean config();\n}'))):
            assert changed!=text
            try:metadata(changed,role)
            except AssertionError:field_negatives.append(role+':'+name)
            else:raise AssertionError('every field/API mutation rejects')
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1834 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1834,physicalAdded=sorted(CLASSES),physicalRemoved=[],physicalChanged={},previousPhysicalUnchanged=1832,originalPhysicalUnchanged=1667,previousManagerPhysicalUnchanged=True,sourceRows=rows,sourceCount=227,currentTests=60,currentSuites=4,newTests=22,necessaryModifiedSourceRegression=38,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],rawPmdFindingsRetained=6,currentClassifiedPmdRows=6,ownerGuardBinding=dict(models=models,roleNegatives=role_negatives,protocolNegatives=protocol_negatives,fieldNegatives=field_negatives,fields=fields,preservedOldTestBodies=preserved_tests),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualPoolConnected=False,managerDynamicPt='UNRUN_HOLD',managerCoverage=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,physical=1834,sourceOwners=227,roleNegatives=len(role_negatives),protocolNegatives=len(protocol_negatives),fieldNegatives=len(field_negatives),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
