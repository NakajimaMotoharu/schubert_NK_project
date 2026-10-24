"""Current cache-only byte change, exact legacy-overload preservation, all Main/owner/static joins."""
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
from api_cleanup_publication_post_contract import qualify,PREFIX
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='fa29009e4fdc97effb40e441110102caf46f3926'
BEFORE='e87ab6ec893fa461dc98e6525e6bbc9885701f32'
SLOT=host.W/'pg9110-api-cleanup-publication-trace-v1'
OUT=host.BASE/'PG9110-api-cleanup-publication-trace-v1'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxCleanupPublicationTest.java'


def protocol(text,old):
    index=text.index('public Optional<Snapshot> observe(ApiReadOnlyObservationAttempt attempt)')
    start=text.rfind('  /**',0,index);end=text.index('  /** Nonblocking invalidation',index)
    assert start>=0 and text[:start]+text[end:]==old
    method=''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text[index:end]).split())
    for required in ('Objects.requireNonNull(attempt,"ownedreadonlyobservationattempt");','synchronized(writerLock){',
      'if(!detailed)returnOptional.empty();','Entrypending=newEntry(Optional.empty());','current.set(pending);',
      'Optional<Snapshot>supplied=Optional.of(attempt.read());','if(current.compareAndSet(pending,newEntry(supplied)))returnsupplied;','returnOptional.empty();'):
        assert required in method
    assert method.count('attempt.read()')==1 and method.index('current.set(pending);')<method.index('attempt.read()')<method.index('current.compareAndSet(')
    for forbidden in ('getConnection(','.commit(','.rollback(','.close(','.start(','.sleep(', 'MeterRegistry','newThread(', 'System.getenv('):assert forbidden not in method


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9104-api-cleanup-publication-six-compile-v1/manifest.json','89b73f7be9b10823da271f53d31e3816b1d74cad616bf2ae07a9b1afe3652da6'),
      'post':('PG9108-api-cleanup-publication-post-v1/manifest.json','b3f6ed290dd8fc0381cf0a9344b761110b28a33816c3b7db6c53b15b32cd4d7f'),
      'review':('PG9107-api-cleanup-publication-lock-review-v1/manifest.json','2f475ac30e7d04d24079ee464fa4c009b7a01e95537727598204239a633b76f2'),
      'priorNormal':('PG9090-api-ro-attempt-union-six-compile-v1/manifest.json','897bae9e89031afe883755b1e502b356b0a76f00ed3a60e505f4f5e974d823ad'),
      'priorOwners':('PG9096-api-ro-attempt-union-trace-v1/manifest.json','287a0941eac016178e2e46b4fc4fe8f60dbfa39d9b8e6087c1169564d809a41b'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest;proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current,review=proof['normal'],proof['post'],proof['review']
    assert normal['source']==SOURCE and normal['actualExit']==0;qualify(current,SOURCE,review)
    hashes=normal['begin']['inputHashes'];snapshot=host.W/'pg9104-api-cleanup-publication-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal);before=base.inventory(proof['priorNormal'])
    assert set(physical)==set(before) and len(physical)==1839
    changed={name for name in before if before[name]!=physical[name]};assert changed=={'api:'+PREFIX+'.class'}
    for name,digest in current['physicalClasses'].items():assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT} and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text();old=subprocess.check_output(['git','show',BEFORE+':'+MAIN],cwd=host.ROOT).decode()
    protocol(text,old);rejected=[]
    for name,a,b in (
      ('no-null-boundary','Objects.requireNonNull(attempt, "owned readonly observation attempt");',''),
      ('no-standard-fence','if (!detailed) return Optional.empty();','if (detailed) return Optional.empty();'),
      ('singleton-pending','Entry pending = new Entry(Optional.empty());','Entry pending = current.get();'),
      ('unguarded-publish','current.compareAndSet(pending, new Entry(supplied))','current.compareAndSet(current.get(), new Entry(supplied))'),
      ('new-io','Optional.of(attempt.read())','Optional.of(attempt.read()); getConnection()'),
      ('old-body-changed','repository.read(connection, asOf)','repository.read(connection, java.time.Instant.EPOCH)')):
        # Mutate the typed overload only, except the intentional legacy-byte guard.
        index=text.index('public Optional<Snapshot> observe(ApiReadOnlyObservationAttempt attempt)')
        mutated=text.replace(a,b,1) if name=='old-body-changed' else text[:index]+text[index:].replace(a,b,1)
        assert mutated!=text
        try:protocol(mutated,old)
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('publication/legacy drift accepted')
    for name,mutate in (
      ('wrong-source',lambda value:value.update(source=BEFORE)),
      ('entry-excluded',lambda value:value['executableClasses'].pop(PREFIX+'$Entry')),
      ('entry-fake-branch',lambda value:value['executableClasses'][PREFIX+'$Entry']['counters']['BRANCH'].update(covered=1)),
      ('raw-pmd-one-hidden',lambda value:value['staticRaw']['pmd'].update(findings=1)),
      ('static-spotbugs',lambda value:value['staticRaw']['spotbugs'].update(findings=1)),
      ('null-unclassified',lambda value:value.update(unclassified=None))):
        mutated=copy.deepcopy(current);mutate(mutated)
        try:qualify(mutated,SOURCE,review)
        except (ValueError,KeyError):rejected.append(name)
        else:raise AssertionError('bad actual post accepted')
    rows=copy.deepcopy(proof['priorOwners']['sourceRows']);assert len(rows)==239 and MAIN in {row['path'] for row in rows} and UNIT not in {row['path'] for row in rows}
    rows.append(dict(path=UNIT));logical={row['path']:row for row in json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    joined=[]
    for row in rows:
        path=row['path'];raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-09')
        resolved=owner.join_rows([raw],logical,hashes,'WBS-P018-09');owner.validate(resolved,[raw],logical,hashes,'WBS-P018-09')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',priorObservationPreserved=True,oldSourcePtTransferred=False);joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==240 and all(row['canonicalOwner'] for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT;reader=SLOT/'reader';reader.mkdir()
    entry=snapshot/'src/schubert-nk-api/target/classes'/(PREFIX+'$Entry.class')
    entry_receipt,byte_text=steps.step('entry-bytecode',[str(architecture.JAVA.parent/'javap'),'-p','-c',str(entry)])
    assert entry_receipt['actualExit']==0 and not re.search(r'\b(if\w*|goto\w*|lookupswitch|tableswitch|jsr\w*)\b',byte_text) and re.search(r'\bputfield\b',byte_text)
    assert current['executableClasses'][PREFIX+'$Entry']['counters']['BRANCH']==dict(missed=0,covered=0)
    compile_receipt,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compile_receipt['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1839 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,
      allPhysicalClassCount=1839,physicalClasses=physical,changedPhysical=sorted(changed),addedPhysical=[],previousPhysicalUnchanged=1838,
      sourceRows=joined,sourceCount=240,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),currentTests=34,currentSuites=2,newTests=14,necessaryRegression=20,
      currentCounters=current['counters'],metadataCounterexamples=rejected,legacyCacheSourceRestoredExactly=True,branchlessEntryNotExcluded=True,entryBytecodeReceipt=entry_receipt,
      architecture=dict(result=analysis,compileReceipt=compile_receipt,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,
      coverageUnion=False,actualProducerSupplied=False,actualDbNativePt='UNRUN_HOLD',ptExecutionExempt=False,whole451Accepted=False,formalUpdated=False,
      newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,allMain=1839,owners=240,newTests=14,necessary=20,metadataNegatives=len(rejected))))


if __name__=='__main__':main()
