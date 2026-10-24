"""All current Main bytes/ownership plus cache identity protocol and real branchless Entry proof."""
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
from api_outbox_source_post_contract import qualify,PREFIX,CLASSES
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='2ed81b14bb41512e1cda720a446ed7b261121605'
BEFORE='73d94fc525c6ea8828ca82d906ec583146fee7bf'
SLOT=host.W/'pg9048-api-outbox-source-trace-v1'
OUT=host.BASE/'PG9048-api-outbox-source-trace-v1'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')


def protocol(text):
    body=''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())
    for expected in ('privatefinalObjectwriterLock=newObject();','privatestaticfinalclassEntry{',
        'privatefinalOptional<Snapshot>observation;','Entry pending=new Entry(Optional.empty());',
        'current.set(pending);','Optional<Snapshot>supplied=Optional.of(repository.read(connection,asOf));',
        'if(current.compareAndSet(pending,newEntry(supplied)))returnsupplied;',
        'publicvoidmissing(){current.set(newEntry(Optional.empty()));}',
        'publicOptional<Snapshot>get(){returncurrent.get().observation;}'):
        assert ''.join(expected.split()) in body
    assert body.count('repository.read(')==1
    assert body.index('current.set(pending);')<body.index('repository.read(')<body.index('current.compareAndSet(')
    for forbidden in ('getConnection(','.commit(','.rollback(','.close(','.start(','.sleep(', 'synchronized(this)', 'MeterRegistry'):
        assert forbidden not in body


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9042-api-outbox-source-six-compile-v1/manifest.json','8680b2ac1059c8acb365d32f48f984124b13d6aeefa0632a6f9a546360290397'),
      'post':('PG9046-api-outbox-source-post-v1/manifest.json','d188fc8a7b0261a0e187d2aeda5f56af783db22f1b7fdcb4f6525685c6d69f14'),
      'review':('PG9045-api-outbox-source-lock-review-v1/manifest.json','5b5d57924ade2b358cc0f7e3d6e5457ec3dd5346fb6392691e31afb86adf4451'),
      'priorNormal':('PG9028-api-service-six-compile-v1/manifest.json','370a39dc80cf8c1cd90997526b6377f1f68aa8b82c7c69b4a04b71c3e66d9f98'),
      'priorOwners':('PG9034-api-service-trace-v3/manifest.json','caf310661eae47595a3b71f5472c052e4c6059e4e31ecdb3e5fead192aa17f4c'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest;proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current,review=proof['normal'],proof['post'],proof['review']
    assert normal['source']==SOURCE and normal['actualExit']==0
    qualify(current,SOURCE,review)
    hashes=normal['begin']['inputHashes'];snapshot=host.W/'pg9042-api-outbox-source-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal);before=base.inventory(proof['priorNormal'])
    added=set(physical)-set(before);changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==1838 and len(before)==1836 and not changed
    assert added=={'api:'+name+'.class' for name in CLASSES}
    for name,digest in current['physicalClasses'].items():assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT}
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text();protocol(text)
    rejected=[]
    for name,old,new in (
        ('singleton-aba','Entry pending = new Entry(Optional.empty());','Entry pending = current.get();'),
        ('unguarded-publication','current.compareAndSet(pending, new Entry(supplied))','current.compareAndSet(current.get(), new Entry(supplied))'),
        ('missing-no-invalidation','current.set(new Entry(Optional.empty()));','current.get();'),
        ('unbounded-read-get','return current.get().observation;','repository.read(connection, asOf); return current.get().observation;'),
        ('borrowed-close','current.set(pending);','connection.close(); current.set(pending);')):
        mutated=text.replace(old,new,1);assert mutated!=text
        try:protocol(mutated)
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('protocol drift accepted')
    for name,mutator in (
        ('unknown-unclassified',lambda value:value.update(unclassified=None)),
        ('branchless-class-excluded',lambda value:value['executableClasses'].pop(PREFIX+'$Entry')),
        ('false-entry-branch',lambda value:value['executableClasses'][PREFIX+'$Entry']['counters']['BRANCH'].update(covered=1)),
        ('missed-entry-method',lambda value:value['executableClasses'][PREFIX+'$Entry']['counters']['METHOD'].update(missed=1)),
        ('raw-pmd-hidden',lambda value:value['staticRaw']['pmd'].update(findings=0)),
        ('unreviewed-row',lambda value:value['staticRaw']['pmd']['rawFindings'][0].update(rule='UNKNOWN'))):
        mutated=copy.deepcopy(current);mutator(mutated)
        try:qualify(mutated,SOURCE,review)
        except (ValueError,KeyError):rejected.append(name)
        else:raise AssertionError('invalid current evidence accepted')
    rows=copy.deepcopy(proof['priorOwners']['sourceRows']);assert len(rows)==235
    assert MAIN not in {row['path'] for row in rows} and UNIT not in {row['path'] for row in rows}
    rows.extend([dict(path=MAIN),dict(path=UNIT)])
    logical={row['path']:row for row in json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    joined=[]
    for row in rows:
        path=row['path'];raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-09')
        resolved=owner.join_rows([raw],logical,hashes,'WBS-P018-09');owner.validate(resolved,[raw],logical,hashes,'WBS-P018-09')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',priorObservationPreserved=True,oldSourcePtTransferred=False)
        joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==237 and all(row['canonicalOwner'] for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT;reader=SLOT/'reader';reader.mkdir()
    entry=snapshot/'src/schubert-nk-api/target/classes'/(PREFIX+'$Entry.class')
    byte_receipt,byte_text=steps.step('entry-bytecode',[str(architecture.JAVA.parent/'javap'),'-p','-c',str(entry)])
    assert byte_receipt['actualExit']==0 and not re.search(r'\b(if\w*|goto\w*|[al]ookupswitch|tableswitch|jsr\w*)\b',byte_text)
    assert re.search(r'\bputfield\b',byte_text) and current['executableClasses'][PREFIX+'$Entry']['counters']['BRANCH']==dict(missed=0,covered=0)
    compile_receipt,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compile_receipt['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1838 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      witnesses=pins,allPhysicalClassCount=1838,physicalClasses=physical,addedPhysical=sorted(added),changedPhysical=[],previousPhysicalUnchanged=1836,
      sourceRows=joined,sourceCount=237,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),currentTests=36,currentSuites=2,newTests=20,necessaryRegression=16,
      currentCounters=current['counters'],branchlessEntry=dict(counter=dict(missed=0,covered=0),bytecodeReceipt=byte_receipt,notExcluded=True),
      metadataCounterexamples=rejected,architecture=dict(result=analysis,compileReceipt=compile_receipt,receipt=checked,targetInitialized=False),
      productTestsExecutedByPost=0,coverageUnion=False,actualProducerSupplied=False,actualDbNativePt='UNRUN_HOLD',ptExecutionExempt=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,allMain=1838,owners=237,newTests=20,necessary=16,metadataNegatives=len(rejected))))


if __name__=='__main__':main()
