"""Current Web/Batch owner scopes, exact descriptors and all-six physical/ownership consistency."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg8696_api_standard_source_lock_trace as api
from host_tool_invocation import capture,verify

host,architecture,steps=api.host,api.architecture,api.steps
SOURCE='4c97764a913a09fd39d9881eb6e112e66c1547e3'
BEFORE='6cd77b76b004e77d0360efee8a62e4553bab05e1'
COMPILE=host.W/'pg8710-web-batch-standard-source-fixed-six-compile-v1'
SLOT=host.W/'pg8716-web-batch-standard-source-trace-v1'
OUT=host.BASE/'PG8716-web-batch-standard-source-trace-v1'
CURRENT_SHA='0321514273cd4f371cc4dc30e599ca846e583d8002581526da6618758227959c'
ROLES={'web':'Web','batch':'Batch'}
MAINS={role:f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}StandardMetricSource.java' for role,title in ROLES.items()}
ADDED=set(MAINS.values())|{path.replace('/main/','/test/').replace('.java','Test.java') for path in MAINS.values()}
POMS={f'src/schubert-nk-{role}/pom.xml' for role in ROLES}
CLASSES={role+':dev/codex/schubert/nk/'+role+'/monitoring/'+title+'StandardMetricSource.class' for role,title in ROLES.items()}

def descriptors(changed):
    assert changed==POMS

def pom(old,new):
    doc=copy.deepcopy(new)
    ns={'m':'http://maven.apache.org/POM/4.0.0'}
    deps=doc.find('m:dependencies',ns)
    added=[node for node in deps if node.findtext('m:artifactId',namespaces=ns)=='micrometer-registry-prometheus']
    assert len(added)==1 and {node.tag.rsplit('}',1)[1]:node.text for node in added[0]}==dict(groupId='io.micrometer',artifactId='micrometer-registry-prometheus',version='1.17.1')
    deps.remove(added[0])
    assert ET.tostring(doc)==ET.tostring(old)

def owner(model,role):
    assert model['package']=='dev.codex.schubert.nk.'+role+'.monitoring' and model['type']==ROLES[role]+'StandardMetricSource'
    assert {'io.micrometer.prometheusmetrics.PrometheusMeterRegistry','java.util.concurrent.locks.ReentrantLock'}<=set(model['imports'])
    forbidden=tuple('dev.codex.schubert.nk.'+other+'.' for other in ('api','web','batch','bootstrap') if other!=role)
    assert not any(name.startswith(forbidden+('java.net.','java.sql.','java.nio.file.')) for name in model['imports'])

def fields(text,role):
    # Same SDK-owned field/API grammar as qualified API owner, exact role name only normalized.
    name=ROLES[role]+'StandardMetricSource'
    normalized=text.replace(name,'ApiStandardMetricSource').replace('dev.codex.schubert.nk.'+role+'.','dev.codex.schubert.nk.api.')
    result=api.metadata(normalized)
    result['actualRole']=role
    result['actualPublicApi']=[line.strip() for line in text.splitlines() if line.startswith('  public ') and line.endswith(';')]
    return result

if __name__=='__main__':
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
        'normal':('PG8710-web-batch-standard-source-fixed-six-compile-v1/manifest.json','d4e08af5550e1da687757e2279f3f4faca6192b50a4de3d7a3efc6dd1d70d374'),
        'current':('PG8714-web-batch-standard-source-post-v1/manifest.json',CURRENT_SHA),
        'priorNormal':('PG8690-api-standard-source-lock-six-compile-v1/manifest.json','b8d281d6662fb915405ac192532d7753abe47a9bf7e53c2a623d217b06a69008'),
        'priorTrace':('PG8696-api-standard-source-lock-trace-v1/manifest.json','aa45bd6f57291f35a1ca7f9c96c94d898f956f07b8a09acd9e5fb870cdbcbd27'),
        'selection':('PG8705-web-batch-external-import-preflight-v1/manifest.json','fac825aca5eb0b8359327b48d248a536a186e53157233761dfd2ff66d05fa7df'),
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
    assert set(after)-set(before)==ADDED and not(set(before)-set(after))
    descriptors({path for path,digest in before.items() if after[path]!=digest})
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    pom_negatives=[]
    for path in sorted(POMS):
        old=api.normalized_xml(subprocess.check_output(['git','show',BEFORE+':'+path],cwd=host.ROOT))
        new=api.normalized_xml((snapshot/path).read_bytes())
        pom(old,new)
        ns={'m':'http://maven.apache.org/POM/4.0.0'}
        for label in ('wrong-version','duplicate-dependency','unrelated-dependency'):
            changed=copy.deepcopy(new)
            deps=changed.find('m:dependencies',ns)
            added=next(node for node in deps if node.findtext('m:artifactId',namespaces=ns)=='micrometer-registry-prometheus')
            if label=='wrong-version':added.find('m:version',ns).text='1.17.2'
            elif label=='duplicate-dependency':deps.append(copy.deepcopy(added))
            else:next(node for node in deps if node is not added).find('m:artifactId',ns).text='forbidden-artifact'
            try:pom(old,changed)
            except AssertionError:pom_negatives.append(path+':'+label)
            else:raise AssertionError('every descriptor dependency mutation rejects')
    for label,changed in (('extra-foreign-pom',POMS|{'src/schubert-nk-api/pom.xml'}),('missing-pom',set(sorted(POMS)[:1]))):
        try:descriptors(changed)
        except AssertionError:pom_negatives.append(label)
        else:raise AssertionError('every descriptor path mutation rejects')
    previous,physical=api.base.inventory(prior),api.base.inventory(normal)
    assert len(previous)==1826 and len(physical)==1828 and set(physical)-set(previous)==CLASSES and all(physical[path]==digest for path,digest in previous.items())
    original=proof['original']['allPhysicalMainSha256']
    assert len(original)==1669 and all(physical[path]==digest for path,digest in original.items())
    for path,digest in current['physicalClasses'].items():
        role=next(role for role in ROLES if path.startswith('dev/codex/schubert/nk/'+role+'/'))
        assert physical[role+':'+path]==digest
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}==dict(dict.fromkeys(ADDED,'A'),**dict.fromkeys(POMS,'M'))
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==209 and POMS<=set(old_rows) and not(set(old_rows)&ADDED)
    rows=[]
    for path in sorted(set(old_rows)|ADDED):
        digest=host.sha(snapshot/path)
        assert path in ADDED|POMS or old_rows[path]['sha256']==digest
        relation='CURRENT_PRIVATE_STANDARD_SOURCE' if path in ADDED else 'CURRENT_FIXED_SDK_DEPENDENCY_POM' if path in POMS else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship=relation))
    assert len(rows)==213
    selection=proof['selection']
    assert selection['source']==SOURCE and selection['actualExit']==0 and len(selection['negativeGuards'])==12
    assert all(host.sha(host.ROOT/row['path'])==row['sha256'] for row in selection['sourceRows'])
    assert host.sha(host.ROOT/'tools/quality/architecture/WebBatchStandardMetricSourceJunitLauncher.java')==selection['helperSha256']
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    models={};role_negatives=[]
    for role,path in MAINS.items():
        body=(snapshot/path).read_text();compact=''.join(body.split())
        model=api.contract.java(body);owner(model,role);models[role]=model
        assert compact.count('lock.lock();try{')==3 and compact.count('finally{lock.unlock();}')==3 and 'synchronized' not in compact
        assert 'newPrometheusMeterRegistry(PrometheusConfig.DEFAULT)' in compact and 'new'+ROLES[role]+'StandardMetrics().bind(source,"DEBUG",owner)' in compact
        expected='newHttpMetricContract().detailedMetricsEnabled(mode)' if role=='web' else 'MonitoringModePolicy.parse(mode).detailedMetricsEnabled()'
        assert expected in compact
        for name,mutate in (('wrong-role',lambda r:r.update(package='dev.codex.schubert.nk.api.monitoring')),('bootstrap-owner',lambda r:r['imports'].append('dev.codex.schubert.nk.bootstrap.metric.Forbidden')),('network-authority',lambda r:r['imports'].append('java.net.ServerSocket'))):
            changed=copy.deepcopy(model);mutate(changed)
            try:owner(changed,role)
            except AssertionError:role_negatives.append(role+':'+name)
            else:raise AssertionError('every role mutation rejects')
    SLOT.mkdir();steps.SLOT=SLOT
    field_rows={};field_negatives=[]
    for role,path in MAINS.items():
        compiled_class=snapshot/path.replace('/src/main/java/','/target/classes/').replace('.java','.class')
        receipt,text=steps.step(role+'-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s',str(compiled_class)])
        assert receipt['actualExit']==0 and not receipt['timedOut']
        actual=fields(text,role)
        prefix='dev.codex.schubert.nk.'+role+'.monitoring.'+ROLES[role]+'StandardMetricSource'
        for name,changed in (('public-lock',text.replace('private final java.util.concurrent.locks.ReentrantLock lock;','public final java.util.concurrent.locks.ReentrantLock lock;')),('public-resource-getter',text.replace('\n}','\n  public io.micrometer.prometheusmetrics.PrometheusMeterRegistry getRegistry();\n}')),('public-test-constructor',text.replace('  '+prefix+'(java.util.function.Supplier','  public '+prefix+'(java.util.function.Supplier'))):
            try:fields(changed,role)
            except AssertionError:field_negatives.append(role+':'+name)
            else:raise AssertionError('every field mutation rejects')
        lock_receipt,code=steps.step(role+'-lock',[str(architecture.JAVA.with_name('javap')),'-p','-c',str(compiled_class)])
        assert lock_receipt['actualExit']==0 and not lock_receipt['timedOut'] and code.count('ReentrantLock.lock:()V')==3 and code.count('ReentrantLock.unlock:()V')>=3 and 'monitorenter' not in code
        field_rows[role]=dict(metadata=actual,receipt=receipt,lockReceipt=lock_receipt)
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1828 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation)
    OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1828,physicalAdded=sorted(CLASSES),physicalRemoved=[],physicalChanged={},previousPhysicalUnchanged=1826,originalPhysicalUnchanged=1669,sourceRows=rows,sourceCount=213,currentTests=32,currentSuites=2,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],ownerGuardBinding=dict(models=models,roleNegatives=role_negatives,fieldNegatives=field_negatives,roleFields=field_rows,descriptorNegatives=pom_negatives,bootstrapSourcesUnchanged=34),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,physical=1828,sourceOwners=213,roleNegatives=len(role_negatives),fieldNegatives=len(field_negatives),descriptorNegatives=len(pom_negatives),architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))
