"""RO one-shot owner all Main/source/canonical ownership and current-quality join, no app init."""
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
from api_ro_union_post_contract import reviewed
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='e87ab6ec893fa461dc98e6525e6bbc9885701f32'
BEFORE='2ed81b14bb41512e1cda720a446ed7b261121605'
SLOT=host.W/'pg9096-api-ro-attempt-union-trace-v1'
OUT=host.BASE/'PG9096-api-ro-attempt-union-trace-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttempt'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')


def protocol(text):
    body=''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())
    for expected in ('privatefinalObjectlock=newObject();','if(attempted)thrownewIllegalStateException(',
        'retained=supplied;','transactionAttempted=true;supplied.setAutoCommit(false);',
        'rollbackAttempted=true;supplied.rollback();closeOwned(supplied);returnresult;',
        'catch(SQLException|RuntimeException|Errorprimary){failures.add(primary);cleanup();',
        'TemporaryInfrastructureException.preserveFatal(primary);throwprimary;',
        'if(transactionAttempted&&!rollbackAttempted)', 'if(!closeAttempted)',
        'closeAttempted=true;try{owned.close();retained=null;}',
        'unconfirmed.set(true);try{onUnconfirmed.accept(close);',
        'publicbooleanhasUnconfirmedResource(){returnunconfirmed.get();}'):
        assert expected in body
    assert body.count('pool.getConnection()')==1 and body.count('repository.read(')==1
    for forbidden in ('throw(RuntimeException)','throwruntime;','newThread(','.commit(','.start(','.sleep(', 'System.err','MeterRegistry','System.getenv('):
        assert forbidden not in body


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9090-api-ro-attempt-union-six-compile-v1/manifest.json','897bae9e89031afe883755b1e502b356b0a76f00ed3a60e505f4f5e974d823ad'),
      'post':('PG9094-api-ro-attempt-union-post-v1/manifest.json','0f882a2d3866a07ae2751e2e9e339753b2c000221e005d2bc48e6c39ba552553'),
      'review':('PG9095-api-ro-attempt-union-context-v1/manifest.json','64157d793d00ab8222dd3380262e2cff6ceb2f32ef216565ca0ebb39f6ab7918'),
      'priorNormal':('PG9042-api-outbox-source-six-compile-v1/manifest.json','8680b2ac1059c8acb365d32f48f984124b13d6aeefa0632a6f9a546360290397'),
      'priorOwners':('PG9048-api-outbox-source-trace-v1/manifest.json','9674bdaea983763fa6c5615ee747657f8bed9cebeeb0a91a0f36ce114ef44ed3'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest;proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current,review=proof['normal'],proof['post'],proof['review']
    assert normal['source']==SOURCE and normal['actualExit']==0
    reviewed(current,SOURCE,32,1,{PREFIX},review)
    hashes=normal['begin']['inputHashes'];snapshot=host.W/'pg9090-api-ro-attempt-union-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal);before=base.inventory(proof['priorNormal'])
    added=set(physical)-set(before);changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==1839 and len(before)==1838 and not changed and added=={'api:'+PREFIX+'.class'}
    for name,digest in current['physicalClasses'].items():assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT}
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text();protocol(text);rejected=[]
    for name,old,new in (
        ('no-adopt','retained = supplied;','retained = null;'),
        ('ambiguous-begin-no-attempt','transactionAttempted = true;','transactionAttempted = false;'),
        ('close-before-rollback','rollbackAttempted = true;','closeAttempted = true;'),
        ('unchecked-cast','throw primary;','throw (RuntimeException) primary;'),
        ('skip-cleanup','cleanup();','hasUnconfirmedResource();'),
        ('false-confirmed','unconfirmed.set(true);','unconfirmed.set(false);'),
        ('no-retry-fence','if (!closeAttempted)','if (closeAttempted)')):
        mutated=text.replace(old,new,1);assert mutated!=text
        try:protocol(mutated)
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('owner protocol drift accepted')
    for old_source in ('42411011d8d7f5e2a70af11a6f8855313adbe1b8','af9868c9ed37e462f9760004066d58d019231aa8','b66e59ede8145586fbe2407881ff342aeee80d31'):
        original=subprocess.check_output(['git','show',old_source+':'+MAIN],cwd=host.ROOT).decode()
        try:protocol(original)
        except (AssertionError,ValueError):rejected.append('original-unqualified-'+old_source)
        else:raise AssertionError('old unqualified propagation accepted')
    for name,mutate in (
        ('wrong-source',lambda value:value.update(source=BEFORE)),
        ('missed-line',lambda value:value['executableClasses'][PREFIX]['counters']['LINE'].update(missed=1)),
        ('missing-unclassified',lambda value:value.pop('unclassified')),
        ('raw-pmd-hidden',lambda value:value['staticRaw']['pmd'].update(findings=0)),
        ('spotbugs-not-zero',lambda value:value['staticRaw']['spotbugs'].update(findings=1)),
        ('unknown-row',lambda value:value['staticRaw']['pmd']['rawFindings'][0].update(rule='UNKNOWN')),
        ('union',lambda value:value.update(coverageUnion=True))):
        mutated=copy.deepcopy(current);mutate(mutated)
        try:reviewed(mutated,SOURCE,32,1,{PREFIX},review)
        except (ValueError,KeyError):rejected.append(name)
        else:raise AssertionError('bad actual post accepted')
    rows=copy.deepcopy(proof['priorOwners']['sourceRows']);assert len(rows)==237
    assert MAIN not in {row['path'] for row in rows} and UNIT not in {row['path'] for row in rows}
    rows.extend([dict(path=MAIN),dict(path=UNIT)])
    logical={row['path']:row for row in json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    joined=[]
    for row in rows:
        path=row['path'];raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-09')
        resolved=owner.join_rows([raw],logical,hashes,'WBS-P018-09');owner.validate(resolved,[raw],logical,hashes,'WBS-P018-09')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',priorObservationPreserved=True,oldSourcePtTransferred=False)
        joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==239 and all(row['canonicalOwner'] for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT;reader=SLOT/'reader';reader.mkdir()
    compile_receipt,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compile_receipt['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1839 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      witnesses=pins,allPhysicalClassCount=1839,physicalClasses=physical,addedPhysical=sorted(added),changedPhysical=[],previousPhysicalUnchanged=1838,
      sourceRows=joined,sourceCount=239,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),currentTests=32,currentSuites=1,newTests=32,necessaryRegression=0,
      currentCounters=current['counters'],metadataCounterexamples=rejected,architecture=dict(result=analysis,compileReceipt=compile_receipt,receipt=checked,targetInitialized=False),
      productTestsExecutedByPost=0,coverageUnion=False,actualProducerSupplied=False,actualDbNativePt='UNRUN_HOLD',ptExecutionExempt=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,allMain=1839,owners=239,newTests=32,metadataNegatives=len(rejected))))


if __name__=='__main__':main()
