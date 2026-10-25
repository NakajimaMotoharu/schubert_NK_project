"""Current Main assembly provenance and partial coverage, never whole-program qualification."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import pg8302_http_cdf_six_trace as base
import trace_owner_join_api_life as previous
import trace_owner_join_api_main as owner
from host_tool_invocation import capture, verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='9f7a3215621dca09184ea24d0ba824b3a002b329'
BEFORE='6c271f74da3e09cbcf52e6c2abf5dd27fe93acd5'
SLOT=host.W/'pg9202-api-main-observation-trace-v1'
OUT=host.BASE/'PG9202-api-main-observation-trace-v1'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiProcessMain'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
TEST=owner.TEST

def compact(text):
    return ''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())

def protocol(text):
    body=compact(text)
    for token in (
      'ApiObservationContext,Boolean,IOException>acquire(',
      'prepareObservations(inputs.config().value("nk.monitoring.mode"),pool,lifetime)',
      'closeObservations(observations,lifetime),true)',
      'observations->{observations.initialize();returnResourceScope.acquire(',
      'outbox::healthy),observations.metrics())',
      'Clock.systemUTC(),System::nanoTime,lifetime::remainingStopNanos,ignored->lifetime.fail(),ServiceProcessResources.unknownReleasePolicy()',
      'Objects.requireNonNull(observations,"APIobservationowner");Objects.requireNonNull(lifetime,"APIlifetimeowner");ResourceScope.',
      '()->observations,ApiObservationContext::close,ignored->{lifetime.stop();returnBoolean.TRUE;}'):
        assert token in body
    assert 'ApiMetricContext' not in body and 'ApiServiceMetricBinding' not in body

def assess(measure,review,raw):
    assert measure['source']==review['source']==raw['source']==SOURCE
    assert measure['actualExit']==review['actualExit']==0 and raw['actualExit']==1
    assert measure['actualTests']==8 and measure['suites']==1
    assert set(measure['exactSelectedCaseIds'])=={'apiObsBoot'+str(i).zfill(3) for i in range(1,9)}
    assert measure['failures']==measure['errors']==measure['skipped']==0 and measure['allDeclaredCasesRun'] is True
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert measure[field] is False
    names={PREFIX,PREFIX+'$Startup',PREFIX+'$ConfigurationLoad'}
    assert set(measure['executableClasses'])==names
    totals={kind:dict(covered=0,missed=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for name,row in measure['executableClasses'].items():
        assert set(row['counters'])==set(totals)
        assert row['recordStatus']==('CURRENT_RECORD' if name==PREFIX else 'DECLARED_INTERFACE_NO_EXECUTABLE_CODE')
        for kind,count in row['counters'].items():
            assert set(count)=={'missed','covered'} and all(type(v) is int and v>=0 for v in count.values())
            if name!=PREFIX: assert not any(count.values())
            for key in count: totals[kind][key]+=count[key]
    assert totals==measure['wholeSourceUnitCounters']
    assert totals==dict(LINE=dict(covered=12,missed=164),METHOD=dict(covered=4,missed=30),
                        CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=0,missed=18))
    assert review['rawPmd']==2 and review['unclassified']==0 and review['programPtComplete'] is False
    assert review['qualityGatePass'] is False and review['ptExecutionExempt'] is False
    canonical=lambda rows:Counter(json.dumps(row,sort_keys=True) for row in rows)
    assert canonical([row['raw'] for row in review['staticDispositions']])==canonical(raw['static']['pmd']['rawFindings'])
    assert raw['static']['pmd']['receipt']['actualExit']==4 and raw['static']['pmd']['findings']==2
    for role in ('pmd','checkstyle','spotbugs'):
        current=raw['static'][role]
        assert current['receipt']['timedOut'] is False and current['processingErrors']==0
        if role!='pmd': assert current['receipt']['actualExit']==0 and current['findings']==0

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9196-api-main-observation-six-compile-v1/manifest.json','4e9f7decf57be45c86e742838802c677e1a61ce9f7f0dcb5b7c7e3999b4d7a4d'),
      'measure':('PG9200-api-main-observation-measure-v1/manifest.json','a38ab05005ceed0609a20589c476e72b17c37a82a51fef3ceecc132ba680dfea'),
      'review':('PG9199-api-main-observation-review-v1/manifest.json','26ace95b0657871b08b95ee7120632bddb21f005a6eb3badc68bcae35fdbe181'),
      'static':('PG9197-api-main-observation-static-v1/manifest.json','aeddd461450c49be5bcfe78b84cb4bad9bd8b6442fbf8fdda56a211c46e5924e'),
      'priorNormal':('PG9182-api-lifetime-budget-six-compile-v2/manifest.json','dc1a8a844dafbed01e8b9beb1123221448ab7e09593b9114efcf98c05e8e057b'),
      'priorOwners':('PG9188-api-lifetime-budget-trace-v1/manifest.json','40935dee125b947b1e53b7b313b0d3f2accf3f1add25be384d842e0e0a4cb75a'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,measure,review,raw=proof['normal'],proof['measure'],proof['review'],proof['static']
    assert normal['source']==SOURCE and normal['actualExit']==0
    assess(measure,review,raw)
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9196-api-main-observation-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); before=base.inventory(proof['priorNormal'])
    changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==len(before)==1843 and set(physical)==set(before)
    assert changed=={'api:'+PREFIX+'.class'}
    for name,digest in measure['physicalClasses'].items(): assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,TEST} and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text(); old=subprocess.check_output(['git','show',BEFORE+':'+MAIN],cwd=host.ROOT).decode()
    protocol(text)
    # Entire business/runtime continuation is byte-token identical despite formatter indentation.
    start='management -> {'; end='groupsReady.set(false);'
    assert compact(old[old.index(start):old.index(end)+len(end)])==compact(text[text.index(start):text.index(end)+len(end)])
    unit=(host.ROOT/TEST).read_text()
    assert len(re.findall(r'(?m)^  @Test$',unit))==8
    assert not any(token in unit for token in ('new ApiProcessMain(','.install(','HookDriver','ProcessBuilder','Runtime.getRuntime'))
    rejected=[]
    for name,scope,mutate in (
      ('wrong-source','measure',lambda v:v.update(source=BEFORE)),
      ('whole100-invented','measure',lambda v:v.update(requiredWholeClassFour100=True)),
      ('metadata-interface-excluded','measure',lambda v:v['executableClasses'].pop(PREFIX+'$Startup')),
      ('coverage-union','measure',lambda v:v.update(coverageUnion=True)),
      ('old-hook-selected','measure',lambda v:v.update(historicalHookOrTermCasesSelected=True)),
      ('unknown-counter','measure',lambda v:v['wholeSourceUnitCounters']['LINE'].update(missed=None)),
      ('static-pass-invented','review',lambda v:v.update(qualityGatePass=True)),
      ('pt-exemption-invented','review',lambda v:v.update(ptExecutionExempt=True)),
      ('raw-row-hidden','review',lambda v:v.update(staticDispositions=[]))):
        values=dict(measure=copy.deepcopy(measure),review=copy.deepcopy(review)); mutate(values[scope])
        try: assess(values['measure'],values['review'],raw)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false qualification accepted')
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    prior=proof['priorOwners']['sourceRows']; assert len(prior)==250
    assert all(previous.canonical(row['path'],logical)==owner.canonical(row['path'],logical) for row in prior)
    assert MAIN in {row['path'] for row in prior} and TEST not in {row['path'] for row in prior}
    assert owner.canonical(MAIN,logical)['canonicalOwner']==owner.canonical(TEST,logical)['canonicalOwner']=='WBS-P018-05'
    joined=[]
    for row in prior+[dict(path=TEST)]:
        path=row['path']; item=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-05')
        resolved=owner.join_rows([item],logical,hashes,'WBS-P018-05'); owner.validate(resolved,[item],logical,hashes,'WBS-P018-05')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',oldSourcePtTransferred=False)
        joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==251
    assert all(row['canonicalOwner'] and row['additionalSharedCostPp']==0 for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256']
    assert host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir(); steps.SLOT=SLOT; reader=SLOT/'reader'; reader.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1843 and len(analysis['rules'])==5 and not analysis['findings'] and all(v==0 for v in analysis['rules'].values())
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,allPhysicalClassCount=1843,physicalClasses=physical,changedPhysical=sorted(changed),
      previousPhysicalUnchanged=1842,addedPhysical=[],sourceRows=joined,sourceCount=251,
      canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),previous250CanonicalMappingsPreserved=True,
      newTests=8,newMain=0,changedSourceUnit=1,currentTests=8,currentSuites=1,businessRuntimeContinuationUnchanged=True,
      wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],requiredWholeClassFour100=False,programPtComplete=False,
      rawPmd=2,reviewedPmd=2,unclassifiedPmd=0,rawStaticExitPreserved=1,metadataCounterexamples=rejected,
      architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),
      productTestsExecutedByTrace=0,coverageUnion=False,actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,
      formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,allMain=1843,owners=251,newTests=8,metadataNegatives=len(rejected),wholeClass100=False)))

if __name__=='__main__':main()
