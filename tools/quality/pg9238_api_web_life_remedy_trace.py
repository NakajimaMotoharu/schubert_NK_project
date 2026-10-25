"""Exact minimum remedy, whole source-unit missed counters, current ownership and architecture."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import pg8302_http_cdf_six_trace as base
import trace_owner_join_api_main as previous_owner
import trace_owner_join_api_web_life as owner
from host_tool_invocation import capture, verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='600b966bab415690bf09d24ba07268a097b19d18'
BEFORE='3641d0f49e6b33fe64de718703f134406dfddb30'
SLOT=host.W/'pg9238-api-web-life-remedy-trace-v1'
OUT=host.BASE/'PG9238-api-web-life-remedy-trace-v1'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.java'
WEB='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime.java'

def compact(text):
    return ''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())

def assess(measure,raw):
    assert measure['source']==raw['source']==SOURCE and measure['actualExit']==0 and raw['actualExit']==1
    assert measure['actualTests']==14 and measure['suites']==3 and measure['newTestIds']==3 and measure['necessaryRegression']==11
    assert measure['failures']==measure['errors']==measure['skipped']==0
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert measure[field] is False
    names={'dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime',
      'dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime$1','dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime'}
    assert set(measure['executableClasses'])==names
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for name,row in measure['executableClasses'].items():
        assert row['recordStatus']==('UNEXECUTED_NO_RECORD_NOT_QUALIFIED' if name.endswith('$1') else 'CURRENT_RECORD')
        assert set(row['counters'])==set(totals)
        for kind,count in row['counters'].items():
            assert all(type(v) is int and v>=0 for v in count.values()) and set(count)=={'missed','covered'}
            for key in count: totals[kind][key]+=count[key]
    assert totals==measure['wholeSourceUnitCounters']
    assert totals==dict(LINE=dict(covered=66,missed=59),METHOD=dict(covered=16,missed=13),
                        CLASS=dict(covered=2,missed=1),BRANCH=dict(covered=14,missed=14))
    for role in ('pmd','checkstyle','spotbugs'):
        current=raw['static'][role]
        assert current['receipt']['timedOut'] is False and current['processingErrors']==0
        assert current['receipt']['actualExit']==(4 if role=='pmd' else 0)
        assert current['findings']==(18 if role=='pmd' else 0)
    rows=raw['static']['pmd']['rawFindings']
    assert not any(row['rule']=='AvoidUsingVolatile' or row['rule']=='EmptyCatchBlock' and row.get('method')=='close' for row in rows)
    assert len(rows)==18

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9232-api-web-life-remedy-six-compile-v1/manifest.json','38ea73ddb99188202104086355e365e61be103eb5f8abc383dfab975f879e219'),
      'measure':('PG9236-api-web-life-remedy-measure-v1/manifest.json','a1e56672716122f40a25ef77764daec7e594195e5689de48ee9dabed01248b99'),
      'static':('PG9235-api-web-life-remedy-static-v1/manifest.json','0c67b6d9c9e74f3b7276bd716f1741957c704cb3f599668f471608fbde9477bc'),
      'priorNormal':('PG9210-api-factory-debug-six-compile-v1/manifest.json','80b8d4f5f4e16723b5871771fcd3bd03bd068e2a59d17cbf1e8d6e8486f3a39b'),
      'previous':('PG9216-api-factory-debug-trace-v1/manifest.json','4fa9a883c89bdef6165bbcf14628b4637736de1a4a5244741f25f7f5b338a77b'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,measure,raw=proof['normal'],proof['measure'],proof['static']
    assess(measure,raw); assert normal['actualExit']==0 and normal['source']==SOURCE
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9232-api-web-life-remedy-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); before=base.inventory(proof['priorNormal'])
    changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==len(before)==1843 and set(physical)==set(before)
    assert changed=={'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.class',
                     'web:dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime.class'}
    for member,digest in measure['physicalClasses'].items():
        role='api' if '/api/' in member else 'web'
        assert physical[role+':'+member]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={API,WEB,owner.TEST}
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    for path in (API,WEB):
        old=compact(subprocess.check_output(['git','show',BEFORE+':'+path],cwd=host.ROOT).decode())
        actual=compact((host.ROOT/path).read_text())
        expected=old.replace('catch(IllegalStateExceptionshutdownInProgress){}','catch(IllegalStateExceptionshutdownInProgress){return;}')
        if path==API:
            expected=expected.replace('privatevolatilebooleaninstalled;','privatefinalAtomicBooleaninstalled=newAtomicBoolean();')
            expected=expected.replace('installed=true;','installed.set(true);').replace('if(installed){installed=false;','if(installed.getAndSet(false)){')
        assert expected!=old and actual==expected
    ordinary=(host.ROOT/owner.TEST).read_text()
    assert ordinary.count('@Test')==3 and not any(token in ordinary for token in ('.install(','.main(','ProcessBuilder','Runtime.getRuntime'))
    rejected=[]
    for name,scope,mutate in (
      ('wrong-source','measure',lambda v:v.update(source=BEFORE)),
      ('whole100-invented','measure',lambda v:v.update(requiredWholeClassFour100=True)),
      ('inner-excluded','measure',lambda v:v['executableClasses'].pop('dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime$1')),
      ('old-coverage-union','measure',lambda v:v.update(coverageUnion=True)),
      ('raw-pmd-hidden','raw',lambda v:v['static']['pmd'].update(findings=0)),
      ('targeted-finding-returned','raw',lambda v:v['static']['pmd']['rawFindings'][0].update(rule='AvoidUsingVolatile')),
      ('old-hook-selected','measure',lambda v:v.update(historicalHookOrTermCasesSelected=True))):
        values=dict(measure=copy.deepcopy(measure),raw=copy.deepcopy(raw)); mutate(values[scope])
        try: assess(**values)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false source quality accepted')
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    prior=proof['previous']['sourceRows']; assert len(prior)==252
    assert all(previous_owner.canonical(row['path'],logical)==owner.canonical(row['path'],logical) for row in prior)
    assert WEB not in {row['path'] for row in prior} and owner.TEST not in {row['path'] for row in prior}
    assert owner.canonical(WEB,logical)['canonicalOwner']==owner.canonical(owner.TEST,logical)['canonicalOwner']=='WBS-P018-06'
    joined=[]
    for row in prior+[dict(path=WEB),dict(path=owner.TEST)]:
        path=row['path']; item=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-05')
        resolved=owner.join_rows([item],logical,hashes,'WBS-P018-05'); owner.validate(resolved,[item],logical,hashes,'WBS-P018-05')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',oldSourcePtTransferred=False); joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==254
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir(); steps.SLOT=SLOT; reader=SLOT/'reader'; reader.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1843 and len(analysis['rules'])==5 and not analysis['findings'] and all(v==0 for v in analysis['rules'].values())
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,allPhysicalClassCount=1843,physicalClasses=physical,
      changedPhysical=sorted(changed),previousPhysicalUnchanged=1841,addedPhysical=[],apiAnonymousInnerBytesUnchanged=True,
      sourceRows=joined,sourceCount=254,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),
      previous252CanonicalMappingsPreserved=True,newTests=3,necessaryRegressionTests=11,currentTests=14,currentSuites=3,newMain=0,
      exactMinimumSourceDelta=True,wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],
      requiredWholeClassFour100=False,programPtComplete=False,rawPmd=18,unclassifiedPmd=18,rawStaticExitPreserved=1,
      targetedVolatileAndCloseEmptyFindings=0,remainingWebInterruptedEmptyCatch=True,
      metadataCounterexamples=rejected,architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),
      productTestsExecutedByTrace=0,coverageUnion=False,actualMainNativePt='UNRUN_HOLD',
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,allMain=1843,owners=254,newTests=3,remainingPmd=18,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
