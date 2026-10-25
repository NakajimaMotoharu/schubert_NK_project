"""Whole Web source unit, exact lock remedy and individual standalone bootstrap applicability."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg8302_http_cdf_six_trace as base
import pg9188_api_lifetime_budget_trace as legacy
import trace_owner_join_api_web_life as owner
from host_tool_invocation import capture, verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
BEFORE='600b966bab415690bf09d24ba07268a097b19d18'
SLOT=host.W/'pg9252-web-life-lock-trace-v1'
OUT=host.BASE/'PG9252-web-life-lock-trace-v1'
WEB='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime.java'
PREFIX='dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime'
UNIT='src/deployment/systemd/schubert-nk-web.service.template'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'

def compact(text):
    return ''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())

def assess(measure,raw):
    assert measure['source']==raw['source']==SOURCE and measure['actualExit']==0 and raw['actualExit']==1
    assert measure['actualTests']==4 and measure['suites']==1 and measure['newTestIds']==1 and measure['necessaryRegression']==3
    assert set(measure['exactSelectedCaseIds'])=={'wlClose'+str(i).zfill(3) for i in range(1,5)}
    assert measure['failures']==measure['errors']==measure['skipped']==0
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert measure[field] is False
    assert set(measure['executableClasses'])=={PREFIX}
    row=measure['executableClasses'][PREFIX]
    assert row['recordStatus']=='CURRENT_RECORD' and row['counters']==measure['wholeSourceUnitCounters']
    assert row['counters']==dict(LINE=dict(covered=30,missed=28),METHOD=dict(covered=7,missed=3),
                                CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=6,missed=8))
    for role in ('pmd','checkstyle','spotbugs'):
        current=raw['static'][role]
        assert current['receipt']['timedOut'] is False and current['processingErrors']==0
        assert current['receipt']['actualExit']==(4 if role=='pmd' else 0)
        assert current['findings']==(8 if role=='pmd' else 0)
    assert Counter(row['rule'] for row in raw['static']['pmd']['rawFindings'])==Counter(DoNotUseThreads=7,CompareObjectsWithEquals=1)

def applicability(rows,text,unit,paths):
    assert Counter(row['rule'] for row in rows)==Counter(DoNotUseThreads=7,CompareObjectsWithEquals=1)
    assert ' dev.codex.schubert.nk.batch.file.RootServiceLauncher WEB' in unit
    assert unit.count('ExecStart=')==1 and 'ExecStart=!/usr/bin/java ' in unit
    assert not any(path.endswith(('.war','.ear','/WEB-INF/web.xml','/META-INF/ejb-jar.xml')) for path in paths)
    assert 'final class WebProcessLifetime implements AutoCloseable' in text
    assert 'Thread.currentThread() == owner' in text
    lines=text.splitlines()
    for row in rows:
        assert row['class']=='WebProcessLifetime' and row['package']=='dev.codex.schubert.nk.web.bootstrap'
        line=lines[int(row['beginline'])-1]
        if row['rule']=='DoNotUseThreads':
            assert line[int(row['begincolumn'])-1:].startswith(('Thread','new Thread'))
        else: assert 'Thread.currentThread() == owner' in line

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'measure':('PG9250-web-life-lock-measure-v1/manifest.json','54fc9529a931f5a7c73802ba7818a5946e3821d24aa9afafafcc202e33227667'),
      'static':('PG9249-web-life-lock-static-v1/manifest.json','f3ab4a4d689eb0ec618eb1247d596c67aaae90dcd5ee4b1257ea82a78ee3b91f'),
      'priorNormal':('PG9232-api-web-life-remedy-six-compile-v1/manifest.json','38ea73ddb99188202104086355e365e61be103eb5f8abc383dfab975f879e219'),
      'previous':('PG9238-api-web-life-remedy-trace-v1/manifest.json','f026b8e6aec316d2408089cafe71910970943c4a8b3ec493c3528541bf0f530c'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,measure,raw=proof['normal'],proof['measure'],proof['static']; assess(measure,raw)
    assert normal['actualExit']==0 and normal['source']==SOURCE
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9246-web-life-lock-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); before=base.inventory(proof['priorNormal'])
    changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==len(before)==1843 and set(physical)==set(before) and changed=={'web:'+PREFIX+'.class'}
    assert measure['physicalClasses']=={PREFIX+'.class':physical['web:'+PREFIX+'.class']}
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={WEB,owner.TEST} and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    old=compact(subprocess.check_output(['git','show',BEFORE+':'+WEB],cwd=host.ROOT).decode())
    text=(host.ROOT/WEB).read_text(); current=compact(text)
    assert current.count('stateLock.lock();try{')==2 and current.count('}finally{stateLock.unlock();}')==2
    restored=current.replace('importjava.util.concurrent.locks.ReentrantLock;','')
    restored=restored.replace('privatefinalReentrantLockstateLock=newReentrantLock();','privatefinalObjectstateLock=newObject();')
    restored=restored.replace('stateLock.lock();try{','synchronized(stateLock){').replace('}finally{stateLock.unlock();}','}')
    restored=restored.replace('catch(InterruptedExceptionnotification){return;}','catch(InterruptedExceptionnotification){}')
    assert restored==old
    old_tests=legacy.cases(subprocess.check_output(['git','show',BEFORE+':'+owner.TEST],cwd=host.ROOT).decode())
    new_tests=legacy.cases((host.ROOT/owner.TEST).read_text())
    assert len(old_tests)==3 and len(new_tests)==4 and all(new_tests[name]==body for name,body in old_tests.items())
    assert set(new_tests)-set(old_tests)=={'wlClose004'}
    rows=raw['static']['pmd']['rawFindings']; unit=(host.ROOT/UNIT).read_text()
    assert host.sha(host.ROOT/UNIT)==hashes[UNIT]
    assert subprocess.check_output(['git','show',FORMAL+':'+SS],cwd=host.ROOT)==(host.ROOT/SS).read_bytes()
    vendor=host.TC/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert host.sha(vendor)==raw['toolHashes'][str(vendor)]=='068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    with zipfile.ZipFile(vendor) as archive:
        rules=ET.fromstring(archive.read('category/java/multithreading.xml'))
    description=' '.join(''.join(next(node for node in rules.findall('{*}rule') if node.get('name')=='DoNotUseThreads').find('{*}description').itertext()).split())
    assert 'J2EE' in description and 'managed' in description
    applicability(rows,text,unit,hashes); rejected=[]
    for name,scope,mutate in (
      ('wrong-source','measure',lambda v:v.update(source=BEFORE)),
      ('whole100-invented','measure',lambda v:v.update(requiredWholeClassFour100=True)),
      ('coverage-union','measure',lambda v:v.update(coverageUnion=True)),
      ('hook-selected','measure',lambda v:v.update(historicalHookOrTermCasesSelected=True)),
      ('raw-pmd-hidden','raw',lambda v:v['static']['pmd'].update(findings=0))):
        values=dict(measure=copy.deepcopy(measure),raw=copy.deepcopy(raw)); mutate(values[scope])
        try: assess(**values)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false coverage acceptance')
    for name,items,body,template,paths in (
      ('unknown-rule',[dict(rows[0],rule='UNKNOWN'),*rows[1:]],text,unit,hashes),
      ('container-role',rows,text,unit,[*hashes,'foreign.war']),
      ('wrong-unit-role',rows,text,unit.replace('RootServiceLauncher WEB','RootServiceLauncher API'),hashes),
      ('owner-identity-lost',rows,text.replace('Thread.currentThread() == owner','Thread.currentThread().equals(owner)'),unit,hashes)):
        try: applicability(items,body,template,paths)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false standalone applicability')
    logical={row['path']:row for row in json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    prior=proof['previous']['sourceRows']; assert len(prior)==254
    joined=[]
    for row in prior:
        path=row['path']; item=dict(path=path,sha256=hashes[path],owner=row['legacyReportedOwner'])
        resolved=owner.join_rows([item],logical,hashes,'WBS-P018-06'); owner.validate(resolved,[item],logical,hashes,'WBS-P018-06')
        assert all(resolved[0][key]==row[key] for key in ('canonicalOwner','canonicalCostOwner','ownershipStatus','basis'))
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',oldSourcePtTransferred=False); joined.extend(resolved)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir(); steps.SLOT=SLOT; reader=SLOT/'reader'; reader.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1843 and not analysis['findings'] and len(analysis['rules'])==5 and all(v==0 for v in analysis['rules'].values())
    decisions=[dict(raw=row,classification='CONTEXT_NOT_APPLICABLE_J2EE_MANAGED_THREADS' if row['rule']=='DoNotUseThreads' else 'EXACT_OWNER_THREAD_IDENTITY_REQUIRED',
      reason='This pinned standalone direct-Java WEB bootstrap owner is not a servlet/container-managed component. Hook waits for this exact owner Thread identity, not value equality. Does not qualify native hook/UNKNOWN execution.',
      sourcePath=WEB,sourceSha256=hashes[WEB],ptExecutionExempt=False,suppressionAdded=False) for row in rows]
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,allPhysicalClassCount=1843,physicalClasses=physical,
      changedPhysical=sorted(changed),previousPhysicalUnchanged=1842,sourceRows=joined,sourceCount=254,
      canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),previous254CanonicalMappingsPreserved=True,
      newTests=1,necessaryRegressionTests=3,currentTests=4,currentSuites=1,newMain=0,old3TestBodiesUnchanged=True,
      exactMinimumSourceDelta=True,unknownRetainingLoopUnchanged=True,unknownIntervalExecuted=False,
      wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],requiredWholeClassFour100=False,programPtComplete=False,
      rawPmd=8,rawStaticExitPreserved=1,staticDispositions=decisions,unclassifiedPmd=0,qualityGatePass=False,
      targetedPrivateSynchronizedAndEmptyFindings=0,unitSha256=hashes[UNIT],formalDesignSource=FORMAL,formalDesignSha256=host.sha(host.ROOT/SS),
      vendorSha256=host.sha(vendor),metadataCounterexamples=rejected,
      architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),
      productTestsExecutedByTrace=0,coverageUnion=False,actualMainNativePt='UNRUN_HOLD',ptExecutionExempt=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,allMain=1843,owners=254,newTests=1,reviewedPmd=8,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
