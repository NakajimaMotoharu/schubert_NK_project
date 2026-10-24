"""All six bytes/owner/public API/private lock of the fixed standard source, no target init."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='6cd77b76b004e77d0360efee8a62e4553bab05e1'
BEFORE='f817b004781e6c32aa2d384dd12855cad7175ddc'
COMPILE=host.W/'pg8690-api-standard-source-lock-six-compile-v1'
SLOT=host.W/'pg8696-api-standard-source-lock-trace-v1'
OUT=host.BASE/'PG8696-api-standard-source-lock-trace-v1'
NORMAL_SHA='b8d281d6662fb915405ac192532d7753abe47a9bf7e53c2a623d217b06a69008'
CURRENT_SHA='8b2e7cf791c2c64434112a459b9d50eb2332602de1d83a7e89e90e6a7234b98d'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSource.java'
UNIT=MAIN.replace('/main/','/test/').replace('.java','Test.java')
POM='src/schubert-nk-api/pom.xml'
CLASS='api:dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSource.class'

def owner(row):
    assert row['package']=='dev.codex.schubert.nk.api.monitoring' and row['type']=='ApiStandardMetricSource'
    assert {'io.micrometer.prometheusmetrics.PrometheusMeterRegistry','java.util.concurrent.locks.ReentrantLock'}<=set(row['imports'])
    assert not any(name.startswith(('dev.codex.schubert.nk.web.','dev.codex.schubert.nk.batch.','dev.codex.schubert.nk.bootstrap.','java.net.','java.sql.','java.nio.file.')) for name in row['imports'])

def metadata(text):
    lines=[line for line in text.splitlines() if line.strip()]
    assert lines[:2]==['Compiled from "ApiStandardMetricSource.java"','public final class dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSource implements java.lang.AutoCloseable {']
    fields=[line for line in lines if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    assert len(fields)==8 and all(line.startswith('  private ') for line in fields)
    assert {line.rsplit(' ',1)[1].removesuffix(';') for line in fields}=={'lock','factory','registration','ownedRegistry','ownedGc','attempted','bound','closed'}
    assert '  private final java.util.concurrent.locks.ReentrantLock lock;' in fields
    public=[line.strip() for line in lines if line.startswith('  public ') and line.endswith(';')]
    assert public==['public dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSource();','public void bind(java.lang.String);','public java.lang.String scrape(java.lang.String);','public void close();']
    return dict(fields=fields,publicApi=public,mutableRegistryPubliclyExposed=False)

def normalized_xml(body):
    doc=ET.fromstring(body)
    for node in doc.iter():
        if node.text is not None and not node.text.strip():node.text=None
        if node.tail is not None and not node.tail.strip():node.tail=None
    return doc

if __name__=='__main__':
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    witnesses={
        'normal':('PG8690-api-standard-source-lock-six-compile-v1/manifest.json',NORMAL_SHA),
        'current':('PG8694-api-standard-source-lock-post-v1/manifest.json',CURRENT_SHA),
        'priorNormal':('PG8632-api-web-custom-payload-six-compile-v1/manifest.json','8039af9b7750d5b689c4663cdb6f02634ad857ed76ad52f6f7d3bba25c0d1c9b'),
        'priorTrace':('PG8638-api-web-custom-payload-six-trace-v1/manifest.json','f8be19c222c4b21a071ff923590f5bea2111b42041b3715c7f6f31e3b28d952c'),
        'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
        'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in witnesses.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current,prior=proof['normal'],proof['current'],proof['priorNormal']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==0 and normal['testsExecuted']==0
    assert current['tests']==16 and current['suites']==1 and len(current['executableClasses'])==1 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and current['coverageUnion'] is False and all(row['missed']==0 for row in current['counters'].values())
    assert prior['source']==proof['priorTrace']['source']==BEFORE
    before,after=prior['begin']['inputHashes'],normal['begin']['inputHashes']
    assert set(after)-set(before)=={MAIN,UNIT} and not(set(before)-set(after))
    assert {path for path,digest in before.items() if after[path]!=digest}=={POM}
    snapshot=COMPILE/'snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    ns={'m':'http://maven.apache.org/POM/4.0.0'}
    old_pom=normalized_xml(subprocess.check_output(['git','show',BEFORE+':'+POM],cwd=host.ROOT))
    new_pom=normalized_xml((snapshot/POM).read_bytes())
    dependencies=new_pom.find('m:dependencies',ns)
    added=[node for node in dependencies if node.findtext('m:artifactId',namespaces=ns)=='micrometer-registry-prometheus']
    assert len(added)==1 and {node.tag.rsplit('}',1)[1]:node.text for node in added[0]}==dict(groupId='io.micrometer',artifactId='micrometer-registry-prometheus',version='1.17.1')
    dependencies.remove(added[0])
    assert ET.tostring(new_pom)==ET.tostring(old_pom)
    previous,physical=base.inventory(prior),base.inventory(normal)
    assert len(previous)==1825 and len(physical)==1826 and set(physical)-set(previous)=={CLASS} and all(physical[path]==digest for path,digest in previous.items())
    original=proof['original']['allPhysicalMainSha256']
    assert len(original)==1669 and all(physical[path]==digest for path,digest in original.items())
    assert current['physicalClasses']['dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSource.class']==physical[CLASS]
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    assert {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}=={MAIN:'A',UNIT:'A',POM:'M'}
    old_rows={row['path']:row for row in proof['priorTrace']['sourceRows']}
    assert len(old_rows)==207 and not(set(old_rows)&{MAIN,UNIT})
    rows=[]
    for path in sorted(set(old_rows)|{MAIN,UNIT}):
        digest=host.sha(snapshot/path)
        assert path in {MAIN,UNIT,POM} or old_rows[path]['sha256']==digest
        relationship='CURRENT_PRIVATE_STANDARD_SOURCE' if path in {MAIN,UNIT} else 'CURRENT_FIXED_SDK_DEPENDENCY_POM' if path==POM else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION'
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship=relationship))
    assert len(rows)==209
    body=(snapshot/MAIN).read_text()
    model=contract.java(body)
    owner(model)
    compact=''.join(body.split())
    assert compact.count('lock.lock();try{')==3 and compact.count('finally{lock.unlock();}')==3 and 'synchronized' not in compact
    assert 'newPrometheusMeterRegistry(PrometheusConfig.DEFAULT)' in compact and 'newApiStandardMetrics().bind(source,"DEBUG",owner)' in compact
    role_rejected=[]
    for name,mutate in (('wrong-role',lambda r:r.update(package='dev.codex.schubert.nk.web.monitoring')),('bootstrap-owner',lambda r:r['imports'].append('dev.codex.schubert.nk.bootstrap.metric.Forbidden')),('network-authority',lambda r:r['imports'].append('java.net.ServerSocket'))):
        changed=copy.deepcopy(model);mutate(changed)
        try:owner(changed)
        except AssertionError:role_rejected.append(name)
        else:raise AssertionError('role negative must reject')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    actual_class=snapshot/MAIN.replace('/src/main/java/','/target/classes/').replace('.java','.class')
    field_receipt,text=steps.step('owner-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s',str(actual_class)])
    assert field_receipt['actualExit']==0 and field_receipt['timedOut'] is False
    fields=metadata(text)
    field_rejected=[]
    for name,changed in (('public-lock',text.replace('private final java.util.concurrent.locks.ReentrantLock lock;','public final java.util.concurrent.locks.ReentrantLock lock;')),('public-resource-getter',text.replace('\n}', '\n  public io.micrometer.prometheusmetrics.PrometheusMeterRegistry getRegistry();\n}')),('public-test-constructor',text.replace('  dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSource(java.util.function.Supplier','  public dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSource(java.util.function.Supplier'))):
        try:metadata(changed)
        except AssertionError:field_rejected.append(name)
        else:raise AssertionError('field/API negative must reject')
    code_receipt,code=steps.step('owner-lock-bytecode',[str(architecture.JAVA.with_name('javap')),'-p','-c',str(actual_class)])
    assert code_receipt['actualExit']==0 and code_receipt['timedOut'] is False and code.count('ReentrantLock.lock:()V')==3 and code.count('ReentrantLock.unlock:()V')>=3 and 'monitorenter' not in code
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    assert checked['actualExit']==0 and analysis['physical']==1826 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in after.items())
    verify(invocation)
    OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=witnesses,physicalClasses=physical,allPhysicalClassCount=1826,physicalAdded=[CLASS],physicalRemoved=[],physicalChanged={},previousPhysicalUnchanged=1825,originalPhysicalUnchanged=1669,sourceRows=rows,sourceCount=209,currentTests=16,currentSuites=1,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],ownerGuardBinding=dict(model=model,roleNegatives=role_rejected,fieldNegatives=field_rejected,fields=fields,fieldReceipt=field_receipt,lockReceipt=code_receipt,bootstrapSourcesUnchanged=34),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1826,sourceOwners=209,roleNegatives=len(role_rejected),fieldNegatives=len(field_rejected),architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))
