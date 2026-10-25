"""Partial Life/source-unit receipt and exact ownership; does not require or invent whole-class PASS."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
import pg8302_http_cdf_six_trace as base
import trace_owner_join_api_stop as previous_owner
import trace_owner_join_api_life as owner
from host_tool_invocation import capture, verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='6c271f74da3e09cbcf52e6c2abf5dd27fe93acd5'
BEFORE='ecfcbf9f6ab81f77301833eda3fba464c72eb4b5'
SLOT=host.W/'pg9188-api-lifetime-budget-trace-v1'
OUT=host.BASE/'PG9188-api-lifetime-budget-trace-v1'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')

def protocol(text):
    compact=''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())
    for token in ('privatefinalApiStopBudgetstopBudget;',
        'ApiProcessLifetime(){this(System::nanoTime);}',
        'ApiProcessLifetime(LongSuppliernanos){stopBudget=newApiStopBudget(nanos);}',
        'voidstop(){retainedStopping.set(true);stopBudget.begin();}',
        'longremainingStopNanos(){returnstopBudget.remainingNanos();}',
        'publicvoidclose(){try{stop();if(installed)',
        'finally{finished.countDown();}'):
        assert token in compact
    assert 'Duration.ofSeconds' not in compact

def assess(measure,review,raw):
    assert measure['source']==review['source']==raw['source']==SOURCE
    assert type(measure['actualExit']) is int and measure['actualExit']==review['actualExit']==0
    assert type(measure['actualTests']) is int and measure['actualTests']==10 and measure['suites']==1
    assert measure['exactSelectedCaseIds']==['lifeBudget'+str(i).zfill(3) for i in range(1,11)]
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert measure[field] is False
    assert measure['failures']==measure['errors']==measure['skipped']==0 and measure['allDeclaredCasesRun'] is True
    names={PREFIX,PREFIX+'$1'}; kinds={'LINE','METHOD','CLASS','BRANCH'}
    assert set(measure['executableClasses'])==names and set(measure['wholeSourceUnitCounters'])==kinds
    totals={kind:dict(missed=0,covered=0) for kind in kinds}
    for name,row in measure['executableClasses'].items():
        assert re.fullmatch('[0-9a-f]{1,16}',row['crc64']) and set(row['counters'])==kinds
        assert row['recordStatus']==('CURRENT_RECORD' if name==PREFIX else 'UNEXECUTED_NO_RECORD_NOT_QUALIFIED')
        for kind,count in row['counters'].items():
            assert set(count)=={'missed','covered'} and all(type(value) is int and value>=0 for value in count.values())
            for key in ('missed','covered'): totals[kind][key]+=count[key]
    assert totals==measure['wholeSourceUnitCounters'] and any(count['missed']>0 for count in totals.values())
    assert review['rawPmd']==9 and review['unclassified']==2 and review['wholeClassStaticAccepted'] is False
    assert review['completeStaticDisposition'] is False
    decisions=review['staticDispositions']; pending=review['unresolvedStaticRows']
    assert len(decisions)==7 and len(pending)==2
    assert {row['raw']['rule'] for row in pending}=={'AvoidUsingVolatile','EmptyCatchBlock'}
    canonical=lambda values:Counter(json.dumps(value,sort_keys=True) for value in values)
    assert canonical([row['raw'] for row in [*decisions,*pending]])==canonical(raw['static']['pmd']['rawFindings'])
    assert raw['static']['pmd']['receipt']['actualExit']==4 and raw['static']['pmd']['findings']==9
    for role in ('pmd','checkstyle','spotbugs'):
        current=raw['static'][role]
        assert current['receipt']['timedOut'] is False and current['processingErrors']==0
        if role!='pmd': assert current['receipt']['actualExit']==0 and current['findings']==0

def cases(text):
    names=re.findall(r'(?ms)^  @Test\n  void (\w+)\(.*?^  }',text)
    values=re.findall(r'(?ms)^  @Test\n  void \w+\(.*?^  }',text)
    assert len(names)==len(values)==len(set(names))
    return dict(zip(names,values,strict=True))

def method(text,name):
    found=list(re.finditer(r'(?m)^  [^\n]*\b'+re.escape(name)+r'\([^)]*\)(?: throws IOException)? \{',text))
    assert len(found)==1
    begin=found[0].start(); brace=text.index('{',found[0].start()); depth=0
    for end in range(brace,len(text)):
        if text[end]=='{': depth+=1
        elif text[end]=='}':
            depth-=1
            if depth==0: return text[begin:end+1]
    raise AssertionError('complete method required')

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9182-api-lifetime-budget-six-compile-v2/manifest.json','dc1a8a844dafbed01e8b9beb1123221448ab7e09593b9114efcf98c05e8e057b'),
      'measure':('PG9186-api-lifetime-budget-measure-v1/manifest.json','d852e44b73825938e8cc6460707475ea75b4831cd7d22d8ba960848a3d0683c5'),
      'review':('PG9185-api-lifetime-budget-partial-review-v1/manifest.json','d64eddc17653bac1849b8c653f9eee1f822a25fe5f7befc59ebe331d17c326f1'),
      'static':('PG9183-api-lifetime-budget-static-v1/manifest.json','9da454967ec0eb9f036dab2b05f73ff29399eb211ee4652b5bbb1a29eb6f6c8f'),
      'priorNormal':('PG9168-api-stop-budget-six-compile-v1/manifest.json','557028d74e26b39a1fa33469e7950419d5e6c3c8b7e04f5479ecb9c1eb8df61c'),
      'priorOwners':('PG9174-api-stop-budget-trace-v2/manifest.json','ebdbb14650b1dca164daf224cd21e503deef005a21946c2876dcfcc82c4c7932'),
      'failedNormal':('PG9182-api-lifetime-budget-six-compile-v1/manifest.json','a99955bb4acdea2adaadfe188d179eac5709650e0a0a1a8463a27ac8437e2354'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,measure,review,raw=proof['normal'],proof['measure'],proof['review'],proof['static']
    assert normal['source']==SOURCE and normal['actualExit']==0
    assess(measure,review,raw)
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9182-api-lifetime-budget-six-compile-v2/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); before=base.inventory(proof['priorNormal'])
    changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==len(before)==1843 and set(physical)==set(before)
    assert changed=={'api:'+PREFIX+'.class','api:'+PREFIX+'$1.class'}
    for name,digest in measure['physicalClasses'].items(): assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT} and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text(); protocol(text); rejected=[]
    for name,old,new in (
      ('begin-before-notification','retainedStopping.set(true);\n    stopBudget.begin();','stopBudget.begin();\n    retainedStopping.set(true);'),
      ('fresh-clock-per-close','return stopBudget.remainingNanos();','return 60_000_000_000L;'),
      ('missing-fixed-constructor','this(System::nanoTime);','this(() -> 0);'),
      ('clock-outside-close-finally','try {\n      stop();','stop();\n    try {')):
        changed_text=text.replace(old,new,1); assert changed_text!=text
        try: protocol(changed_text)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('bad Life budget protocol accepted')
    for name,scope,mutate in (
      ('wrong-source','measure',lambda value:value.update(source=BEFORE)),
      ('whole100-invented','measure',lambda value:value.update(requiredWholeClassFour100=True)),
      ('inner-omitted','measure',lambda value:value['executableClasses'].pop(PREFIX+'$1')),
      ('unknown-counter','measure',lambda value:value['executableClasses'][PREFIX]['counters']['LINE'].update(missed=None)),
      ('old-record-union','measure',lambda value:value.update(coverageUnion=True)),
      ('legacy-hook-added','measure',lambda value:value.update(historicalHookOrTermCasesSelected=True)),
      ('pending-normalized','review',lambda value:value.update(unclassified=0)),
      ('pending-dropped','review',lambda value:value.update(unresolvedStaticRows=[]))):
        values=dict(measure=copy.deepcopy(measure),review=copy.deepcopy(review)); mutate(values[scope])
        try: assess(values['measure'],values['review'],raw)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false partial-scope acceptance allowed')
    old_main=subprocess.check_output(['git','show',BEFORE+':'+MAIN],cwd=host.ROOT).decode()
    for name in ('install','stopping','fail','committedFailureHandler','guardSync','guardEvent','checkRunning','await','shutdown'):
        assert method(old_main,name)==method(text,name)
    old_unit=subprocess.check_output(['git','show',BEFORE+':'+UNIT],cwd=host.ROOT).decode()
    current_unit=(host.ROOT/UNIT).read_text(); old_cases=cases(old_unit); current_cases=cases(current_unit)
    new_cases={name:value for name,value in current_cases.items() if name.startswith('lifeBudget')}
    assert len(new_cases)==10 and all(current_cases[name]==value for name,value in old_cases.items())
    assert all(not any(word in body for word in ('install(','HookDriver','ProcessBuilder','Runtime.getRuntime')) for body in new_cases.values())
    original_test=subprocess.check_output(['git','show','77b2d3bd7081232100958037ca88bf12083bf596:'+UNIT],cwd=host.ROOT).decode()
    original_cases=cases(original_test)
    changed_cases={name for name in original_cases if original_cases[name]!=current_cases[name]}
    assert changed_cases=={'lifeBudget005'}
    assert current_unit.replace(current_cases['lifeBudget005'],original_cases['lifeBudget005'],1)==original_test
    assert 'try (var lifetime' in original_cases['lifeBudget005'] and 'try (var lifetime' not in current_cases['lifeBudget005']
    assert subprocess.check_output(['git','show','77b2d3bd7081232100958037ca88bf12083bf596:'+MAIN],cwd=host.ROOT)==text.encode()
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    previous=copy.deepcopy(proof['priorOwners']['sourceRows']); assert len(previous)==248
    assert all(previous_owner.canonical(row['path'],logical)==owner.canonical(row['path'],logical) for row in previous)
    assert MAIN in logical and UNIT not in logical
    assert owner.canonical(MAIN,logical)['canonicalOwner']==owner.canonical(UNIT,logical)['canonicalOwner']=='WBS-P018-05'
    assert owner.canonical(UNIT,logical)['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
    assert MAIN not in {row['path'] for row in previous} and UNIT not in {row['path'] for row in previous}
    joined=[]
    for row in previous+[dict(path=MAIN),dict(path=UNIT)]:
        path=row['path']; input_row=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-05')
        resolved=owner.join_rows([input_row],logical,hashes,'WBS-P018-05'); owner.validate(resolved,[input_row],logical,hashes,'WBS-P018-05')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',priorObservationPreserved=True,oldSourcePtTransferred=False); joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==250 and all(row['canonicalOwner'] for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir(); steps.SLOT=SLOT; reader=SLOT/'reader'; reader.mkdir()
    old_inner=SLOT/'old-inner.class'; current_inner=host.W/'pg9186-api-lifetime-budget-measure-v1/ApiProcessLifetime$1.class'
    with zipfile.ZipFile(proof['priorNormal']['jars']['api']['path']) as archive:
        with old_inner.open('xb') as stream: stream.write(archive.read(PREFIX+'$1.class'))
    javap=host.TC/'jdk-25.0.4/bin/javap'
    first,old_code=steps.step('old-inner-code',[str(javap),'-c','-p',str(old_inner)])
    second,new_code=steps.step('current-inner-code',[str(javap),'-c','-p',str(current_inner)])
    assert first['actualExit']==second['actualExit']==0 and old_code==new_code
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1843 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,
      allPhysicalClassCount=1843,physicalClasses=physical,changedPhysical=sorted(changed),addedPhysical=[],previousPhysicalUnchanged=1841,
      anonymousInnerCodeUnchangedDebugOnly=True,innerCodeReceipts=[first,second],oldExecutableCoverageTransferred=False,
      sourceRows=joined,sourceCount=250,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),
      previous248CanonicalMappingsPreserved=True,newOwnerBasis='Main original485 P01805; exact existing Life Test responsibility P01805, no historical cost reassignment',
      newTests=10,newMain=0,changedSourceUnit=1,currentTests=10,currentSuites=1,legacyTestBodiesUnchanged=True,
      compilerCorrectionOnlyCase005=True,other9NewCasesPreserved=True,metadataCounterexamples=rejected,
      wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],requiredWholeClassFour100=False,programPtComplete=False,
      rawPmd=9,reviewedPmd=7,unclassifiedPmd=2,wholeStaticAccepted=False,
      architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),
      productTestsExecutedByTrace=0,coverageUnion=False,actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,allMain=1843,owners=250,newTests=10,metadataNegatives=len(rejected),wholeClass100=False,unclassifiedPmd=2)))

if __name__=='__main__':main()
