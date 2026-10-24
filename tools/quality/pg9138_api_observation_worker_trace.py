"""Current worker source/run/all Main/ownership; historical failures and oracle changes stay explicit."""
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
from api_observation_worker_post_contract import reviewed
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='fdc229c9a7b7759cea106d1126c8da0f27a70e09'
BEFORE='f82e3e1ee6d6090b1b81222d18fd35366d0637c1'
SLOT=host.W/'pg9138-api-observation-worker-trace-v1'
OUT=host.BASE/'PG9138-api-observation-worker-trace-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')


def protocol(text):
    body=''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())
    for expected in ('privatefinalObjectstartLock=newObject();','worker=newThread(this::run,"nk-api-observation");',
        'starting.set(true);','starter.accept(worker);','starting.set(false);startReturned.countDown();',
        'wake.tryAcquire(1,TimeUnit.SECONDS)&&!stopping.get()',
        'Thread.currentThread()==worker||unconfirmedStop.get()',
        'if(firstRemaining<=0)thrownewIOException(UNCONFIRMED);',
        'Math.min(firstRemaining-elapsed,remainingNanos.getAsLong())',
        'if(elapsed<0||remaining<=0)thrownewIOException(UNCONFIRMED);',
        'if(!startReturned.await(remaining,TimeUnit.NANOSECONDS))thrownewIOException(UNCONFIRMED);',
        'if(!worker.join(Duration.ofNanos(remaining)))thrownewIOException(UNCONFIRMED);',
        'if(!pump.isQuiescent())thrownewIOException(UNCONFIRMED);','unconfirmedStop.set(true);',
        'if(interrupted)Thread.currentThread().interrupt();',
        'System.err.println("NK_API_OBSERVATION_WORKER_FAILED");'):
        assert expected in body
    assert body.count('starter.accept(worker);')==body.count('longfirstRemaining=')==1
    assert body.index('longfirstRemaining=')<body.index('if(firstRemaining<=0)')<body.index('longbegan=nanos.getAsLong();')
    for forbidden in ('unconfirmedStop.set(false)','getConnection(','.commit(','.rollback(','.getMessage(','.printStackTrace(', 'System.getenv('):assert forbidden not in body


def cases(text):
    rows=re.findall(r'(?ms)^  @Test\n  void (obsOwn\d{3})\(.*?^  }',text)
    values=re.findall(r'(?ms)^  @Test\n  void obsOwn\d{3}\(.*?^  }',text)
    assert len(rows)==len(values)==len(set(rows))==44
    return dict(zip(rows,values,strict=True))


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9132-api-observation-worker-six-compile-v4/manifest.json','e0ffc872d61a2eb6b4556de13eabcd0173e957ed9b832d2df29088f6308e4ac1'),
      'post':('PG9136-api-observation-worker-post-v1/manifest.json','24632ab8560ae2cf33785fff6868987375fb6e8d2a1de4e9cd8e7a9fdf0b3a12'),
      'review':('PG9135-api-observation-worker-context-v1/manifest.json','c1be834044f886aaf6f92ce619da09f1e9a3c00923afa8cd387b105b3415b44b'),
      'canaries':('PG9137-worker-boundary-canaries-v2/manifest.json','7cdbc517b96c3b00874121af6be266b0c94c34e79ad3c628e5ad002f746164a4'),
      'priorNormal':('PG9118-api-outbox-pump-six-compile-v2/manifest.json','23bbd17c711949852ec9c71b7a7cf49caeef26f917e8f13328c4680c92fd0227'),
      'priorOwners':('PG9124-api-outbox-pump-trace-v1/manifest.json','e24df0881bc6057c9d2e05e68334ee382ceac184b9564722f36ebfb49375d9f7'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest;proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current,review=proof['normal'],proof['post'],proof['review']
    assert normal['source']==SOURCE and normal['actualExit']==0
    reviewed(current,SOURCE,44,1,{PREFIX},review)
    assert proof['canaries']['actualExit']==0 and proof['canaries']['source']==SOURCE and proof['canaries']['productTestsExecuted']==0
    assert len(proof['canaries']['compilerCanaries'])==3 and len(proof['canaries']['metadataCounterexamples'])==12
    hashes=normal['begin']['inputHashes'];snapshot=host.W/'pg9132-api-observation-worker-six-compile-v4/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal);before=base.inventory(proof['priorNormal'])
    added=set(physical)-set(before);changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==1841 and len(before)==1840 and not changed and added=={'api:'+PREFIX+'.class'}
    for name,digest in current['physicalClasses'].items():assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT} and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text();protocol(text);rejected=[]
    for name,a,b in (
      ('not-tracking-start','starting.set(true);','starting.set(false);'),
      ('negative-budget-not-guarded','firstRemaining <= 0','firstRemaining < 0'),
      ('renewed-stop-budget','firstRemaining - elapsed','remainingNanos.getAsLong()'),
      ('unchecked-latch-result','if (!startReturned.await(remaining, TimeUnit.NANOSECONDS))','if (startReturned.await(remaining, TimeUnit.NANOSECONDS))'),
      ('unchecked-join-result','if (!worker.join(Duration.ofNanos(remaining)))','if (worker.join(Duration.ofNanos(remaining)))'),
      ('stop-without-quiescence','if (!pump.isQuiescent())','if (pump.isQuiescent())'),
      ('unknown-normalized','unconfirmedStop.set(true);','unconfirmedStop.set(false);'),
      ('name-not-identity','Thread.currentThread() == worker','Thread.currentThread().getName().equals(worker.getName())')):
        mutated=text.replace(a,b,1);assert mutated!=text
        try:protocol(mutated)
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('worker protocol drift accepted')
    for name,mutate in (
      ('wrong-source',lambda value:value.update(source=BEFORE)),
      ('unknown-counter',lambda value:value['executableClasses'][PREFIX]['counters']['BRANCH'].update(missed=None)),
      ('missing-unclassified',lambda value:value.pop('unclassified')),
      ('pmd-hidden',lambda value:value['staticRaw']['pmd'].update(findings=0)),
      ('spotbugs-not-zero',lambda value:value['staticRaw']['spotbugs'].update(findings=1)),
      ('unknown-rule',lambda value:value['staticRaw']['pmd']['rawFindings'][0].update(rule='UNKNOWN')),
      ('union',lambda value:value.update(coverageUnion=True))):
        mutated=copy.deepcopy(current);mutate(mutated)
        try:reviewed(mutated,SOURCE,44,1,{PREFIX},review)
        except (ValueError,KeyError):rejected.append(name)
        else:raise AssertionError('bad actual post accepted')
    original_unit=subprocess.check_output(['git','show','ecd3fd0e6a060744e4a2dc50fb84fb1abd27c5fb:'+UNIT],cwd=host.ROOT).decode()
    unit=(host.ROOT/UNIT).read_text();old_cases=cases(original_unit);new_cases=cases(unit)
    changed_cases={name for name in old_cases if old_cases[name]!=new_cases[name]};assert changed_cases=={'obsOwn025','obsOwn042'}
    restored=unit
    for name in changed_cases:restored=restored.replace(new_cases[name],old_cases[name],1)
    assert restored==original_unit
    assert 'assertEquals(2, clock.get());' in new_cases['obsOwn025'] and 'assertEquals(2, limits.get());' in new_cases['obsOwn025']
    serial_fix=subprocess.check_output(['git','diff','--name-only','3524cbbe0e6d2b2e1c116181d517579c99e96fb2','e155e239a548ed1b99cfe42710cbf6da2056e1a2','--','src'],cwd=host.ROOT,text=True).splitlines()
    assert serial_fix==[UNIT]
    rows=copy.deepcopy(proof['priorOwners']['sourceRows']);assert len(rows)==242 and MAIN not in {row['path'] for row in rows} and UNIT not in {row['path'] for row in rows}
    rows.extend([dict(path=MAIN),dict(path=UNIT)]);logical={row['path']:row for row in json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    joined=[]
    for row in rows:
        path=row['path'];raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-09')
        resolved=owner.join_rows([raw],logical,hashes,'WBS-P018-09');owner.validate(resolved,[raw],logical,hashes,'WBS-P018-09')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',priorObservationPreserved=True,oldSourcePtTransferred=False);joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==244 and all(row['canonicalOwner'] for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT;reader=SLOT/'reader';reader.mkdir()
    compile_receipt,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compile_receipt['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1841 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,
      allPhysicalClassCount=1841,physicalClasses=physical,addedPhysical=sorted(added),changedPhysical=[],previousPhysicalUnchanged=1840,
      sourceRows=joined,sourceCount=244,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),currentTests=44,currentSuites=1,newTests=44,necessaryRegression=0,
      currentCounters=current['counters'],metadataCounterexamples=rejected,changedOracleCases=sorted(changed_cases),other42CasesAndFixtureRestoredExactly=True,
      serialFixWasTestOnly=True,boundaryCanariesNotProductTests=True,
      architecture=dict(result=analysis,compileReceipt=compile_receipt,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,
      coverageUnion=False,privateJvmWorkerTestOnly=True,actualMainNativePt='UNRUN_HOLD',ptExecutionExempt=False,whole451Accepted=False,formalUpdated=False,
      newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,allMain=1841,owners=244,newTests=44,metadataNegatives=len(rejected),other42TestsPreserved=True)))


if __name__=='__main__':main()
