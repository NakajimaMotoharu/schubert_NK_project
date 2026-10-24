"""Current235 canonical source rows, all1836 Main bytes, new38 proof and source-only caller PG."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import pg8302_http_cdf_six_trace as base
import trace_owner_join as owner
from selected_post_contract import clean
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='73d94fc525c6ea8828ca82d906ec583146fee7bf'
BEFORE='f690fa6be336550f8078e2bdde40ef34ab5efe6b'
SLOT=host.W/'pg9034-api-service-trace-v3'
OUT=host.BASE/'PG9034-api-service-trace-v3'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiServiceMetricBinding.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')
CALLER='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java'
HTTP='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandlerTest.java'
CADDY='src/deployment/caddy/Caddyfile.template'


def compact(text):return ''.join(text.split())


def protocol(text):
    body=compact(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text))
    for required in ['returnprepareContext(mode,pool,config,Optional::<Snapshot>empty);',
        'privatefinalApiDbPoolMetricBindingdatabase;','privatefinalOutboxRowsMetricRecorderrows;',
        'privatefinalOutboxAgeMetricRecorderages;','privatefinalSupplier<?extendsOptional<Snapshot>>observations;',
        'newApiMetricContext<ApiServiceMetricBinding>(', 'ApiServiceMetricBinding::refresh',
        'booleancomplete=false;', 'finally{if(!complete)missing();}', 'returnlastObservation.get();']:
        assert required in body
    assert body.count('pool.get()')==body.count('config.get()')==body.count('observations.get()')==1
    positions=[body.index(value) for value in ['database.refresh();','observations.get()','rows.record(value.counts());','ages.record(value.ages());','lastObservation.set(supplied);','complete=true;']]
    assert positions==sorted(positions)
    assert len(re.findall(r'\bpublic\s+(?:static\s+)?[^(){};]+?\(',text))==3
    for forbidden in ('getConnection(', 'prepareStatement(', '.commit(', '.rollback(', '.close(', '.start(', 'newThread(', 'System.getenv('):
        assert forbidden not in body


def caller(text,old):
    restored=text.replace('ApiServiceMetricBinding','ApiDbPoolMetricBinding')
    imports=lambda value:set(re.findall(r'^import[^;]+;',value,re.M))
    assert imports(restored)==imports(old)
    assert compact(re.sub(r'^import[^;]+;','',restored,flags=re.M))==compact(re.sub(r'^import[^;]+;','',old,flags=re.M))
    literal=lambda value:Counter(re.findall(r'"(?:\\.|[^"\\])*"',value))
    assert literal(text)==literal(old)


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9028-api-service-six-compile-v1/manifest.json','370a39dc80cf8c1cd90997526b6377f1f68aa8b82c7c69b4a04b71c3e66d9f98'),
      'post':('PG9032-api-service-post-v1/manifest.json','4585f25047cd5f657152facf8486a44a69fe73c67d17345b864cd61e3965a358'),
      'priorNormal':('PG9014-caddy-format-six-compile-v1/manifest.json','01bad7736bbef335cb0b8dee60947e5767d57180bb59c631ae4ea9374058c18c'),
      'priorOwners':('PG8958-canonical-owner-join-v1/manifest.json','208fa4cd2ecb4ca62631fae6cc60ebaef39abd410edd64da00f4d3a29f244755'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest;proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current=proof['normal'],proof['post']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==current['actualExit']==0
    assert current['tests']==38 and current['suites']==2 and len(current['executableClasses'])==2
    assert all(counter['missed']==0 for counter in current['counters'].values())
    clean(current,SOURCE,38,2,{'dev/codex/schubert/nk/api/monitoring/ApiServiceMetricBinding','dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandler'})
    hashes=normal['begin']['inputHashes'];snapshot=host.W/'pg9028-api-service-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal);before=base.inventory(proof['priorNormal'])
    added=set(physical)-set(before);changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==1836 and len(before)==1835
    assert added=={'api:dev/codex/schubert/nk/api/monitoring/ApiServiceMetricBinding.class'}
    assert changed=={'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.class'}
    for name,digest in current['physicalClasses'].items():assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT,CALLER,HTTP}
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text();protocol(text)
    caller((host.ROOT/CALLER).read_text(),subprocess.check_output(['git','show',BEFORE+':'+CALLER],cwd=host.ROOT).decode())
    http=(host.ROOT/HTTP).read_text();index=http.index('  void apimhttp022')
    start=http.rfind('  @Test\n',0,index);end=http.index('  private static ApiMetricContext<String> standard()',index)
    assert start>=0 and http[:start]+http[end:]==subprocess.check_output(['git','show',BEFORE+':'+HTTP],cwd=host.ROOT).decode()
    negatives=[]
    for name,before_text,after_text in [('default-missing','Optional::<Snapshot>empty','Optional::<Snapshot>ofNullable'),
        ('strong-rows','private final OutboxRowsMetricRecorder rows;','private OutboxRowsMetricRecorder rows;'),
        ('skip-source','observations.get()','Optional.<Snapshot>empty()'),
        ('primary-finally','if (!complete) missing();','if (complete) missing();'),
        ('false-snapshot','lastObservation.set(supplied);','lastObservation.set(Optional.empty());'),
        ('new-io','database.refresh();','database.refresh(); getConnection();'),
        ('double-source','observations.get()','observations.get().or(() -> observations.get())')]:
        mutated=text.replace(before_text,after_text,1);assert mutated!=text
        try:protocol(mutated)
        except (AssertionError,ValueError):negatives.append(name)
        else:raise AssertionError('metadata protocol drift accepted')
    logical_file=host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    logical={row['path']:row for row in json.loads(logical_file.read_bytes())['artifacts']}
    rows=copy.deepcopy(proof['priorOwners']['sourceRows']);assert len(rows)==232
    known={row['path'] for row in rows};assert MAIN not in known and UNIT not in known and CADDY not in known
    rows += [dict(path=MAIN),dict(path=UNIT),dict(path=CADDY)]
    joined=[]
    for row in rows:
        path=row['path'];raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or ('WBS-C01' if path==CADDY else 'WBS-P018-09'))
        change_owner='WBS-C01' if path==CADDY else 'WBS-P018-09'
        resolved=owner.join_rows([raw],logical,hashes,change_owner)
        owner.validate(resolved,[raw],logical,hashes,change_owner)
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',
             priorObservationPreserved=True,oldSourcePtTransferred=False)
        joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==235 and all(row['canonicalOwner'] for row in joined)
    counts=Counter(row['canonicalOwner'] for row in joined)
    assert counts==Counter({'WBS-P018-09':215,'WBS-C07':8,'WBS-F02':4,'WBS-C02':1,'WBS-C06':1,'WBS-P018-05':2,'WBS-P018-06':3,'WBS-C01':1})
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT;reader=SLOT/'reader';reader.mkdir()
    compile_receipt,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compile_receipt['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1836 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
         witnesses=pins,allPhysicalClassCount=1836,physicalClasses=physical,addedPhysical=sorted(added),changedPhysical=sorted(changed),
         previousPhysicalUnchanged=1834,sourceRows=joined,sourceCount=235,canonicalOwnerCounts=dict(counts),
         currentTests=38,currentSuites=2,newTests=17,necessaryRegression=21,currentCounters=current['counters'],
         metadataProtocolCounterexamples=negatives,old21TestBodiesPreserved=True,callerRestoresOldBusinessSourceExactly=True,
         realSqlSamplerAdded=False,defaultOutboxSource='UNSUPPLIED_OPTIONAL_EMPTY_NAN_NOT_ZERO',
         architecture=dict(result=analysis,compileReceipt=compile_receipt,receipt=checked,targetInitialized=False),
         productTestsExecutedByPost=0,coverageUnion=False,callerDynamicPt='UNRUN_HOLD',callerCoverage=None,
         ptExecutionExempt=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
         actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,allPhysicalMain=1836,sourceRows=235,newTests=17,necessaryRegression=21,architectureRules=len(analysis['rules']),architectureFindings=0)))


if __name__=='__main__':main()
