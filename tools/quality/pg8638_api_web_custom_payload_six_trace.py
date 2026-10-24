"""Pure ready/custom two-role source, physical bytes, fixed prefix and limited owner proof."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture, verify

host, architecture, steps = base.host, base.architecture, base.steps
SOURCE = 'f817b004781e6c32aa2d384dd12855cad7175ddc'
BEFORE = 'e81adb96849e4067beb12f212350ab4fbd4b1998'
COMPILE = host.W / 'pg8632-api-web-custom-payload-six-compile-v1'
SLOT = host.W / 'pg8638-api-web-custom-payload-six-trace-v1'
OUT = host.BASE / 'PG8638-api-web-custom-payload-six-trace-v1'
ROLES = {'api':'ApiCustomMetricPayload', 'web':'WebCustomMetricPayload'}
PATHS = {role:f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{name}.java' for role,name in ROLES.items()}
ADDED = set(PATHS.values()) | {p.replace('/main/','/test/').replace('.java','Test.java') for p in PATHS.values()}
CLASSES = {f'{role}:dev/codex/schubert/nk/{role}/monitoring/{name}.class' for role,name in ROLES.items()}
WITNESSES = (
 ('normal','PG8632-api-web-custom-payload-six-compile-v1/manifest.json','8039af9b7750d5b689c4663cdb6f02634ad857ed76ad52f6f7d3bba25c0d1c9b'),
 ('current','PG8636-api-web-custom-payload-post-v1/manifest.json','e2062ef8e44f0ec3a4e758179c78c24bbe946afde4d738129363643ea9c5b1a9'),
 ('priorNormal','PG8608-web-batch-standard-assembly-six-compile-v1/manifest.json','4033792b291efa7bbcb2403c4fdd81bd459c206d3b2bfe619e1488dff6bc44a3'),
 ('priorTrace','PG8614-web-batch-standard-assembly-six-trace-v1/manifest.json','4db5de17bef3a3931514591195f72133d5355b98d922ac0c2f39ac218e67afba'),
 ('gapAudit','PG8628-c07-current-hook-audit-v1/manifest.json','f3bdedbd8c8a760256dc665b82f9ca14e2b5523a6a699b51dc3c5dc01311892a'),
 ('selection','PG8633-api-web-custom-payload-selection-preflight-v1/manifest.json','25cb9d0e1668ebfc38ebb1e8df42bc71c3e0bb218f4afc0bcf295b06f14922fa'),
 ('originalRun','PG8634-api-web-custom-payload-host-v1/manifest.json','5f09c33d46e0a3a9de6ab0259a0fd4c110e2aff7c95570f9cc6ed4cfebbeafac'),
 ('original','PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
 ('architecture','PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))

require = base.require

def owner(row, role):
    require(row['package']=='dev.codex.schubert.nk.'+role+'.monitoring' and row['type']==ROLES[role], 'fixed pure payload role/type')
    forbidden = tuple('dev.codex.schubert.nk.'+other+'.' for other in ('api','web','batch','bootstrap') if other!=role)
    require({'io.micrometer.core.instrument.MeterRegistry','java.util.function.Supplier'}<=set(row['imports']) and not any(p.startswith(forbidden+('java.net.','com.sun.net.httpserver.','java.sql.')) for p in row['imports']), 'borrowed pure source only, no other app/shared/network/DB authority')

def ready_prefix(role):
    return '# TYPE schubert_nk_'+role+'_ready gauge\nschubert_nk_'+role+'_ready '

def fields(text, role):
    lines=[line for line in text.splitlines() if line.strip()]
    name=ROLES[role]
    require(lines[:2]==['Compiled from "'+name+'.java"','public final class dev.codex.schubert.nk.'+role+'.monitoring.'+name+' {'] and lines[-1]=='}','exact class grammar')
    result=[(line,lines[i+1]) for i,line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    expected='  private static final java.lang.String READY_PREFIX = '+json.dumps(ready_prefix(role))+';'
    require(result==[(expected,'    descriptor: Ljava/lang/String;')], 'fixed same-role literal prefix only, no retained instance state')
    return result

def main():
    invocation=capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(),'new-only exact source proof')
    proofs,pins={},{}
    for key,path,digest in WITNESSES:
        require(host.sha(host.BASE/path)==digest,'immutable '+key)
        proofs[key]=json.loads((host.BASE/path).read_text())
        pins[key]=dict(path=path,sha256=digest)
    normal,current,prior=proofs['normal'],proofs['current'],proofs['priorNormal']
    require(normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==0 and normal['testsExecuted']==0,'same source actual normal/current qualification')
    require(current['tests']==26 and current['suites']==2 and len(current['executableClasses'])==2 and current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values()),'original26/2 actual two-class four100')
    require(prior['source']==proofs['priorTrace']['source']==proofs['gapAudit']['source']==BEFORE and prior['actualExit']==proofs['priorTrace']['actualExit']==proofs['gapAudit']['actualExit']==0,'qualified prior source and current hook gap evidence')
    before,after=prior['begin']['inputHashes'],normal['begin']['inputHashes']
    require(set(after)-set(before)==ADDED and not(set(before)-set(after)) and all(after[p]==h for p,h in before.items()),'only four additive source files; old endpoints/startup/formatters/POM identical')
    snapshot=COMPILE/'snapshot'
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in after.items()),'all frozen/current source input bytes')
    previous,physical=base.inventory(prior),base.inventory(normal)
    require(len(previous)==1823 and len(physical)==1825 and set(physical)-set(previous)==CLASSES and all(physical[p]==h for p,h in previous.items()),'two new physical classes; all prior1823 raw/debug unchanged')
    original=proofs['original']['allPhysicalMainSha256']
    require(len(original)==1669 and all(physical[p]==h for p,h in original.items()),'original1669 unchanged, no historical PT transfer')
    for path,digest in current['physicalClasses'].items():
        role=next((r for r in ROLES if path.startswith('dev/codex/schubert/nk/'+r+'/')),None)
        require(role is not None and physical[role+':'+path]==digest,'exact selected physical owner bytes')
    delta=subprocess.check_output(['git','diff','--no-renames','--name-status','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT).split(b'\0')[:-1]
    require(len(delta)==8 and {delta[i+1].decode():delta[i].decode() for i in range(0,len(delta),2)}==dict.fromkeys(ADDED,'A'),'exact four added Main/Unit paths')
    old_rows={r['path']:r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows)==203 and not(set(old_rows)&ADDED),'all prior203 source owners')
    rows=[]
    for path in sorted(set(old_rows)|ADDED):
        digest=host.sha(snapshot/path)
        require(path in ADDED or old_rows[path]['sha256']==digest,'old source owner same bytes')
        rows.append(dict(path=path,sha256=digest,owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_READY_CUSTOM_SOURCE' if path in ADDED else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION',sourceUnchanged=path not in ADDED))
    require(len(rows)==207 and proofs['priorTrace']['ownerGuardBinding']['bootstrapSourcesUnchanged']==34,'all207 owners and limited Bootstrap unchanged')
    models,rejected={},[]
    legacy=[]
    for role in ROLES:
        body=(snapshot/PATHS[role]).read_text()
        model=contract.java(body)
        owner(model,role)
        compact=''.join(body.split())
        title='Api' if role=='api' else 'Web'
        require(body.count('source.get()')==1 and 'new'+title+'MetricScrape().scrape(' in compact and '.close(' not in body,'one supplied source borrowed into approved own-role formatter, no close')
        literal=json.dumps(ready_prefix(role))
        require(literal in body,'fixed legacy-ready literal in current source')
        server=f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{title}ManagementServer.java'
        require(literal in (snapshot/server).read_text() and before[server]==after[server],'same legacy endpoint byte literal and unchanged old management server')
        legacy.append(dict(path=server,sha256=after[server],prefix=ready_prefix(role)))
        models[role]=model
        for label,change in (('wrong-owner',lambda r:r.update(package='dev.codex.schubert.nk.batch.monitoring')),('shared-bootstrap',lambda r:r['imports'].append('dev.codex.schubert.nk.bootstrap.metric.FORBIDDEN')),('network-authority',lambda r:r['imports'].append('java.net.ServerSocket'))):
            mutant=copy.deepcopy(model);change(mutant)
            try: owner(mutant,role)
            except ValueError: rejected.append(role+':'+label)
            else: raise ValueError('every role responsibility negative rejects')
    selection=proofs['selection'];helper=str(host.ROOT/'tools/quality/architecture/ApiWebCustomMetricPayloadJunitLauncher.java')
    require(selection['source']==SOURCE and selection['actualExit']==0 and len(selection['selected'])==2 and len(selection['negatives'])==3 and selection['productTestsExecuted']==0 and selection['helperSha256']==proofs['originalRun']['begin']['testSourceHashes'][helper]==host.sha(Path(helper)),'exact new launcher preflight used by original26')
    require(host.sha(architecture.SOURCE)==proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA,'same canary-qualified noninitializing bytecode reader')
    SLOT.mkdir();steps.SLOT=SLOT
    field_rows,field_negatives={},[]
    for role,name in ROLES.items():
        receipt,text=steps.step(role+'-fields',[str(architecture.JAVA.with_name('javap')),'-p','-s','-constants',str(snapshot/PATHS[role].replace('/src/main/java/','/target/classes/').replace('.java','.class'))])
        require(receipt['actualExit']==0,'actual compiled field metadata terminal')
        actual=fields(text,role)
        anchor='  public dev.codex.schubert.nk.'+role+'.monitoring.'+name+'();'
        for label,mutant in (
            ('retained-source',text.replace(anchor,'  private final io.micrometer.core.instrument.MeterRegistry source;\n    descriptor: Lio/micrometer/core/instrument/MeterRegistry;\n'+anchor)),
            ('public-prefix',text.replace('private static final java.lang.String','public static final java.lang.String',1)),
            ('wrong-descriptor',text.replace('descriptor: Ljava/lang/String;','descriptor: Ljava/lang/Object;',1)),
            ('foreign-prefix',text.replace('schubert_nk_'+role+'_ready','schubert_nk_batch_ready'))):
            try: fields(mutant,role)
            except ValueError: field_negatives.append(role+':'+label)
            else: raise ValueError('every field/prefix negative rejects')
        field_rows[role]=dict(fields=actual,instanceFieldCount=0,fixedPrefixConstantCount=1,receipt=receipt)
    require(len(rejected)==6 and len(field_negatives)==8,'six role and eight exact field/prefix negatives')
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    require(compiled['actualExit']==0,'architecture reader compilation')
    checked,text=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(text)
    require(checked['actualExit']==0 and analysis['physical']==1825 and not analysis['findings'] and len(analysis['rules'])==5 and all(v==0 for v in analysis['rules'].values()),'all1825 and five actual architecture edges zero')
    require(all(host.sha(snapshot/p)==h and host.sha(host.ROOT/p)==h for p,h in after.items()),'all source inputs unchanged after metadata proof')
    verify(invocation)
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,physicalClasses=physical,allPhysicalClassCount=1825,physicalAdded=sorted(CLASSES),physicalRemoved=[],physicalChanged={},previousPhysicalUnchanged=1823,originalPhysicalUnchanged=1669,sourceRows=rows,sourceCount=207,currentTests=26,currentSuites=2,currentExecutableScope=sorted(current['executableClasses']),currentCounters=current['counters'],legacyEndpointUnchanged=legacy,selectionGuard=selection,ownerGuardBinding=dict(currentRoleModels=models,newNegativeGuards=rejected,roleFields=field_rows,fieldNegatives=field_negatives,bootstrapSourcesUnchanged=34,descriptorsUnchanged=True,metadataOnly=True),architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,sourceByteOnlyRowsNotCurrentPtPass=True,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1825,sourceOwners=207,roleNegatives=6,fieldNegatives=8,legacyEndpointsUnchanged=2,architecture=analysis['rules'],manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
