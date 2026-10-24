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
from api_outbox_pump_post_contract import reviewed
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='f82e3e1ee6d6090b1b81222d18fd35366d0637c1'
BEFORE='fa29009e4fdc97effb40e441110102caf46f3926'
SLOT=host.W/'pg9124-api-outbox-pump-trace-v1'
OUT=host.BASE/'PG9124-api-outbox-pump-trace-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')


def protocol(text):
    body=''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())
    for expected in ('privatefinalObjectlock=newObject();','Duration.ofSeconds(15)',
        'if(!detailed||stopping.get()||unconfirmed.get()||active.get())return;',
        'if(previouslyClaimed&&now-lastClaim<intervalNanos)return;',
        'retained.set(Optional.of(attempt));','if(!stopping.get())source.observe(attempt);',
        'retained.get().map(ApiReadOnlyObservationAttempt::hasUnconfirmedResource).orElse(false)',
        'unconfirmed.set(true);','if(stopping.get())source.missing();','active.set(false);',
        'publicvoidrequestStop(){stopping.set(true);source.missing();}',
        'return!active.get()&&!unconfirmed.get();','if(stopping.get()||unconfirmed.get())returnOptional.empty();'):
        assert expected in body
    assert body.count('attempts.get()')==body.count('nanos.getAsLong()')==1
    assert body.index('retained.set(Optional.of(attempt));')<body.index('source.observe(attempt);')
    for forbidden in ('newThread(','.start(','.join(','.sleep(','.getConnection(','.commit(','.rollback(','.close(', 'System.err','System.getenv('):
        assert forbidden not in body


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    pins={
      'draftNormal':('PG9118-api-outbox-pump-six-compile-v1/manifest.json','d55f4efdc8789b8ab569a109ab66a1b6cb30eda2d4f629efce7080839eda89d6'),
      'normal':('PG9118-api-outbox-pump-six-compile-v2/manifest.json','23bbd17c711949852ec9c71b7a7cf49caeef26f917e8f13328c4680c92fd0227'),
      'post':('PG9122-api-outbox-pump-post-v1/manifest.json','d1393a7fee14afe4b246823db1268873cbfb30cd2aa8e280534b41738f023edc'),
      'review':('PG9121-api-outbox-pump-context-v1/manifest.json','2a65576e7ac6ff097fa0010e05a5ec08c6afe15b601b9b6abdf0da23bd93db20'),
      'priorNormal':('PG9104-api-cleanup-publication-six-compile-v1/manifest.json','89b73f7be9b10823da271f53d31e3816b1d74cad616bf2ae07a9b1afe3652da6'),
      'priorOwners':('PG9110-api-cleanup-publication-trace-v1/manifest.json','0e74d487c28358ab9e5c74645e0dd45be6762f1b76a02294edb3b7ed8a6d5083'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest;proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current,review=proof['normal'],proof['post'],proof['review']
    assert normal['source']==SOURCE and normal['actualExit']==0
    reviewed(current,SOURCE,32,1,{PREFIX},review)
    hashes=normal['begin']['inputHashes'];snapshot=host.W/'pg9118-api-outbox-pump-six-compile-v2/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal);before=base.inventory(proof['priorNormal'])
    assert base.inventory(proof['draftNormal'])==physical and proof['draftNormal']['testsExecuted']==0
    old_inputs=proof['draftNormal']['begin']['inputHashes']
    assert set(old_inputs)==set(hashes) and {path for path in hashes if hashes[path]!=old_inputs[path]}=={UNIT}
    added=set(physical)-set(before);changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==1840 and len(before)==1839 and not changed and added=={'api:'+PREFIX+'.class'}
    for name,digest in current['physicalClasses'].items():assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT}
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text();protocol(text);rejected=[]
    for name,old,new in (
        ('wrong-period','Duration.ofSeconds(15)','Duration.ofSeconds(1)'),
        ('boundary-off-by-one','now - lastClaim < intervalNanos','now - lastClaim <= intervalNanos'),
        ('no-unknown-fence','unconfirmed.get() || active.get()','active.get()'),
        ('owner-not-held','retained.set(Optional.of(attempt));','retained.set(Optional.empty());'),
        ('false-quiescence','return !active.get() && !unconfirmed.get();','return !active.get();'),
        ('late-stop-output','if (stopping.get() || unconfirmed.get()) return Optional.empty();','if (unconfirmed.get()) return Optional.empty();'),
        ('new-worker','source.observe(attempt);','source.observe(attempt); new Thread();')):
        mutated=text.replace(old,new,1);assert mutated!=text
        try:protocol(mutated)
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('pump protocol drift accepted')
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
    rows=copy.deepcopy(proof['priorOwners']['sourceRows']);assert len(rows)==240
    assert MAIN not in {row['path'] for row in rows} and UNIT not in {row['path'] for row in rows}
    rows.extend([dict(path=MAIN),dict(path=UNIT)])
    logical={row['path']:row for row in json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    joined=[]
    for row in rows:
        path=row['path'];raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-09')
        resolved=owner.join_rows([raw],logical,hashes,'WBS-P018-09');owner.validate(resolved,[raw],logical,hashes,'WBS-P018-09')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',priorObservationPreserved=True,oldSourcePtTransferred=False)
        joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==242 and all(row['canonicalOwner'] for row in joined)
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT;reader=SLOT/'reader';reader.mkdir()
    compile_receipt,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compile_receipt['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1840 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      witnesses=pins,allPhysicalClassCount=1840,physicalClasses=physical,addedPhysical=sorted(added),changedPhysical=[],previousPhysicalUnchanged=1839,
      sourceRows=joined,sourceCount=242,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),currentTests=32,currentSuites=1,newTests=32,necessaryRegression=0,
      currentCounters=current['counters'],metadataCounterexamples=rejected,architecture=dict(result=analysis,compileReceipt=compile_receipt,receipt=checked,targetInitialized=False),
      productTestsExecutedByPost=0,coverageUnion=False,actualProducerSupplied=False,workerOrSchedulerCreated=False,pumpOnlyNotOwnedStop=True,actualDbNativePt='UNRUN_HOLD',ptExecutionExempt=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,allMain=1840,owners=242,newTests=32,metadataNegatives=len(rejected))))


if __name__=='__main__':main()
