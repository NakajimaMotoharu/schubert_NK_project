"""Current assembly bytes/owners/architecture and defect-origin guards; no runtime acceptance."""
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
from api_observation_context_post_contract import reviewed
from host_tool_invocation import capture, verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='cb91bc2ec0ef5a36652369aff5c86fa037801cca'
BEFORE='fdc229c9a7b7759cea106d1126c8da0f27a70e09'
SLOT=host.W/'pg9160-api-observation-context-trace-v1'
OUT=host.BASE/'PG9160-api-observation-context-trace-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/ApiObservationContext'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')

def protocol(text):
    compact=''.join(text.split())
    for expected in ('privatefinalApiMetricContext<?>metricContext;',
        'metricContext.initialize();','worker.ifPresent(OwnedApiObservationWorker::start);',
        'stopping.set(true);','worker.ifPresent(OwnedApiObservationWorker::requestStop);',
        'lock.isHeldByCurrentThread()||!lock.tryLock()','if(unconfirmed.get())thrownewIOException(UNCONFIRMED);',
        'worker.orElseThrow().awaitStopped(remainingNanos);','metricContext.close();',
        'unconfirmed.set(true);','onUnconfirmed.accept(primary);',
        'TemporaryInfrastructureException.attachSecondary(primary,diagnostic);',
        'TemporaryInfrastructureException.preserveFatal(primary);','throwprimary;','returnmetricContext;'):
        assert expected in compact
    assert compact.index('awaitStopped(remainingNanos);')<compact.index('metricContext.close();')
    for bad in ('Duration.ofSeconds','pool.close(','getConnection(','catch(NullPointerException','unconfirmed.set(false)'):
        assert bad not in compact

def helper_contract(text,expected):
    compact=''.join(text.split())
    for name in ('value.getTestsFoundCount()','value.getTestsStartedCount()','value.getTestsSucceededCount()','results.size()'):
        assert compact.count(name+'=='+str(expected))==1
    assert 'dev.codex.schubert.nk.api.monitoring.ApiObservationContextTest' in text

def cases(text):
    names=re.findall(r'(?ms)^  @Test\n  void (obsCtx\d{3})\(.*?^  }',text)
    values=re.findall(r'(?ms)^  @Test\n  void obsCtx\d{3}\(.*?^  }',text)
    assert len(names)==len(values)==len(set(names))==26
    return dict(zip(names,values,strict=True))

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9154-api-observation-context-six-compile-v3/manifest.json','3ad165657e7b7dda87fc795b505063b2276b64b34b521fcb09070b3c68d7c5fd'),
      'post':('PG9158-api-observation-context-post-v1/manifest.json','f2729d1e3eb68429dd43494d1ab737bd878dc08e113c963932197a2f6abbd385'),
      'review':('PG9157-api-observation-context-review-v1/manifest.json','a728b7c177342e3d6f9931daa0b1b8bd3d2fcdf10bc8c2977c7bb33014e17eb6'),
      'priorNormal':('PG9132-api-observation-worker-six-compile-v4/manifest.json','e0ffc872d61a2eb6b4556de13eabcd0173e957ed9b832d2df29088f6308e4ac1'),
      'priorOwners':('PG9138-api-observation-worker-trace-v1/manifest.json','68dd79441376d60e705e0856e3e0077c59a40f7f76c6d9cace1b0e5045c10d37'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current,review=proof['normal'],proof['post'],proof['review']
    assert normal['source']==SOURCE and normal['actualExit']==0
    reviewed(current,SOURCE,26,1,{PREFIX},review)
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9154-api-observation-context-six-compile-v3/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); previous=base.inventory(proof['priorNormal'])
    added=set(physical)-set(previous); changed={name for name in previous if previous[name]!=physical[name]}
    assert len(physical)==1842 and len(previous)==1841 and not changed and added=={'api:'+PREFIX+'.class'}
    for name,digest in current['physicalClasses'].items(): assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT} and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text(); protocol(text); rejected=[]
    for name,old,new in (
      ('renews-budget','awaitStopped(remainingNanos)','awaitStopped(System::nanoTime)'),
      ('loses-unknown-state','unconfirmed.set(true);','unconfirmed.set(false);'),
      ('normalizes-primary','throw primary;','return;'),
      ('loses-policy-fatal','TemporaryInfrastructureException.attachSecondary(primary, diagnostic);',''),
      ('sdk-before-drain','metricContext.close();','pool.close();'),
      ('blocking-reentrant-close','lock.isHeldByCurrentThread() || !lock.tryLock()','!lock.tryLock()'),
      ('same-field-getter','private final ApiMetricContext<?> metricContext;','private final ApiMetricContext<?> metrics;')):
        mutated=text.replace(old,new,1); assert mutated!=text
        try: protocol(mutated)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('bad assembly protocol accepted')
    for name,mutate in (
      ('wrong-source',lambda value:value.update(source=BEFORE)),
      ('unknown-counter',lambda value:value['executableClasses'][PREFIX]['counters']['BRANCH'].update(missed=None)),
      ('missing-unclassified',lambda value:value.pop('unclassified')),
      ('pmd-hidden',lambda value:value['staticRaw']['pmd'].update(findings=0)),
      ('spotbugs-not-zero',lambda value:value['staticRaw']['spotbugs'].update(findings=1)),
      ('union',lambda value:value.update(coverageUnion=True))):
        mutated=copy.deepcopy(current); mutate(mutated)
        try: reviewed(mutated,SOURCE,26,1,{PREFIX},review)
        except (ValueError,KeyError): rejected.append(name)
        else: raise AssertionError('bad actual post accepted')
    initial='ca4254abd2517d41a84b832bc9c09a980b96c4de'
    original_unit=subprocess.check_output(['git','show',initial+':'+UNIT],cwd=host.ROOT).decode()
    unit=(host.ROOT/UNIT).read_text(); old_cases=cases(original_unit); new_cases=cases(unit)
    changed_cases={name for name in old_cases if old_cases[name]!=new_cases[name]}; assert changed_cases=={'obsCtx016'}
    assert unit.replace(new_cases['obsCtx016'],old_cases['obsCtx016'],1)==original_unit
    assert 'observation worker stop unconfirmed' in new_cases['obsCtx016'] and 'assertSame(first, f.unknown.peek());' in new_cases['obsCtx016']
    corrected_unit=subprocess.check_output(['git','show','c06a72ef46bb65c091de329468f70dd5d347ce4e:'+UNIT],cwd=host.ROOT)
    assert corrected_unit==unit.encode()
    old_main=subprocess.check_output(['git','show',initial+':'+MAIN],cwd=host.ROOT).decode()
    renamed=old_main.replace('private final ApiMetricContext<?> metrics;','private final ApiMetricContext<?> metricContext;').replace('this.metrics =','this.metricContext =').replace('metrics.initialize();','metricContext.initialize();').replace('metrics.close();','metricContext.close();').replace('return metrics;','return metricContext;')
    assert renamed==text
    helper=host.ROOT/'tools/quality/architecture/ApiObservationContextJunitLauncherV2.java'
    helper_contract(helper.read_text(),26)
    old_helper=host.ROOT/'tools/quality/architecture/ApiObservationContextJunitLauncher.java'
    try: helper_contract(old_helper.read_text(),26)
    except AssertionError: rejected.append('old44-launcher-rejected-for26')
    else: raise AssertionError('old44 launcher accepted')
    wrong=helper.read_text().replace('getTestsSucceededCount() == 26','getTestsSucceededCount() == 25',1)
    assert wrong!=helper.read_text()
    try: helper_contract(wrong,26)
    except AssertionError: rejected.append('one-summary-count-drift')
    else: raise AssertionError('wrong summary accepted')
    naming=[]; examined=0
    for role in ('api','web','batch'):
        folder=host.ROOT/f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring'
        for path in folder.rglob('*.java'):
            source=path.read_text(); examined+=1
            fields=set(re.findall(r'(?m)^  private (?:final )?[\w<?>., ]+ (\w+)\s*(?:[=;])',source))
            getters=set(re.findall(r'(?m)^  public [\w<?>., ]+ (\w+)\(\)',source))
            if fields&getters: naming.append(dict(path=str(path.relative_to(host.ROOT)),names=sorted(fields&getters),sha256=host.sha(path)))
    assert examined==113 and len(naming)==1 and naming[0]['names']==['detailedMetricsEnabled','retentionBytes','retentionDays']
    scalar=(host.ROOT/naming[0]['path']).read_text()
    assert 'public enum MonitoringModePolicy' in scalar and all(token in scalar for token in ('private final boolean detailedMetricsEnabled;','private final int retentionDays;','private final long retentionBytes;'))
    naming[0].update(disposition='UNRELATED_ENUM_SCALAR_VALUES_NOT_BORROWED_RESOURCE_OWNER',wholeClassStaticQualifiedByThisSearch=False)
    rows=copy.deepcopy(proof['priorOwners']['sourceRows']); assert len(rows)==244
    assert MAIN not in {row['path'] for row in rows} and UNIT not in {row['path'] for row in rows}
    rows.extend([dict(path=MAIN),dict(path=UNIT)])
    logical={row['path']:row for row in json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    joined=[]
    for row in rows:
        path=row['path']; raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-09')
        resolved=owner.join_rows([raw],logical,hashes,'WBS-P018-09'); owner.validate(resolved,[raw],logical,hashes,'WBS-P018-09')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',priorObservationPreserved=True,oldSourcePtTransferred=False); joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==246 and all(row['canonicalOwner'] for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir(); steps.SLOT=SLOT; reader=SLOT/'reader'; reader.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1842 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,
      allPhysicalClassCount=1842,physicalClasses=physical,addedPhysical=sorted(added),changedPhysical=[],previousPhysicalUnchanged=1841,
      sourceRows=joined,sourceCount=246,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),
      currentTests=26,currentSuites=1,newTests=26,necessaryRegression=0,currentCounters=current['counters'],metadataCounterexamples=rejected,
      changedOracleCases=sorted(changed_cases),other25CasesAndCommonFixturePreserved=True,productMainFixOnlyHeldFieldRename=True,
      launcherCurrentExpectedTests=26,oldLauncherExpectedTests=44,namingSearchFiles=examined,namingCandidates=naming,
      architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,
      coverageUnion=False,actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,allMain=1842,owners=246,newTests=26,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
