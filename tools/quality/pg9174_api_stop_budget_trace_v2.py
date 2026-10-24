"""API stop budget bytes/explicit P01805 ownership; metadata and bytecode import only."""
from collections import Counter
import copy
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import trace_owner_join as previous_owner
import trace_owner_join_api_stop as owner
from api_stop_budget_post_contract_v2 import reviewed
from host_tool_invocation import capture, verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE='ecfcbf9f6ab81f77301833eda3fba464c72eb4b5'
BEFORE='cb91bc2ec0ef5a36652369aff5c86fa037801cca'
SLOT=host.W/'pg9174-api-stop-budget-trace-v2'
OUT=host.BASE/'PG9174-api-stop-budget-trace-v2'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiStopBudget'
MAIN='src/schubert-nk-api/src/main/java/'+PREFIX+'.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')

def protocol(text):
    compact=''.join(text.split())
    for token in ('privatefinalObjectlock=newObject();','TimeUnit.SECONDS.toNanos(60)',
        'if(begun)return;','begun=true;','began=time();','if(!begun)thrownewIllegalStateException',
        'if(expired)return0;','longelapsed=time()-began;','elapsed<0||elapsed>=LIMIT_NANOS',
        'returnLIMIT_NANOS-elapsed;','if(!returned)expired=true;'):
        assert token in compact
    assert compact.index('begun=true;')<compact.index('began=time();')
    assert compact.count('synchronized(lock)')==2
    for forbidden in ('newThread','getConnection(','.close(','.start(','expired=false','catch(NullPointerException'):
        assert forbidden not in compact

def main():
    invocation=capture(Path(__file__)); assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG9168-api-stop-budget-six-compile-v1/manifest.json','557028d74e26b39a1fa33469e7950419d5e6c3c8b7e04f5479ecb9c1eb8df61c'),
      'post':('PG9172-api-stop-budget-post-v1/manifest.json','cf2f8da6e5bf93466eb2e96ad47aaf3ffb70998d5310461e8d2332e4f10d284c'),
      'review':('PG9171-api-stop-budget-review-v1/manifest.json','b80b4184cc24ad6264aee4855225f7aebd8baff87cae77f265e649842e2b7f8b'),
      'priorNormal':('PG9154-api-observation-context-six-compile-v3/manifest.json','3ad165657e7b7dda87fc795b505063b2276b64b34b521fcb09070b3c68d7c5fd'),
      'priorOwners':('PG9160-api-observation-context-trace-v1/manifest.json','33d6811f8d10422d348f404c8269f689295c1e57f0dbd3e033b9e312e61849f1'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,current,review=proof['normal'],proof['post'],proof['review']
    assert normal['source']==SOURCE and normal['actualExit']==0
    reviewed(current,SOURCE,18,1,{PREFIX},review)
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9168-api-stop-budget-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); before=base.inventory(proof['priorNormal'])
    added=set(physical)-set(before); changed={name for name in before if before[name]!=physical[name]}
    assert len(physical)==1843 and len(before)==1842 and not changed and added=={'api:'+PREFIX+'.class'}
    for name,digest in current['physicalClasses'].items(): assert physical['api:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT} and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    text=(host.ROOT/MAIN).read_text(); protocol(text); rejected=[]
    for name,old,new in (
      ('renewed-cap','TimeUnit.SECONDS.toNanos(60)','TimeUnit.SECONDS.toNanos(120)'),
      ('repeat-notification-restarts','if (begun) return;',''),
      ('claim-not-frozen','begun = true;','begun = false;'),
      ('signed-reverse-revives','elapsed < 0','elapsed > 0'),
      ('exact-deadline-not-expired','elapsed >= LIMIT_NANOS','elapsed > LIMIT_NANOS'),
      ('clock-failure-not-sticky','if (!returned) expired = true;',''),
      ('unlimited-prebegin','if (!begun) throw new IllegalStateException','if (begun) throw new IllegalStateException')):
        changed=text.replace(old,new,1); assert changed!=text
        try: protocol(changed)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('bad stop budget accepted')
    for name,mutate in (
      ('wrong-source',lambda value:value.update(source=BEFORE)),
      ('unknown-counter',lambda value:value['executableClasses'][PREFIX]['counters']['BRANCH'].update(missed=None)),
      ('missing-unclassified',lambda value:value.pop('unclassified')),
      ('pmd-hidden',lambda value:value['staticRaw']['pmd'].update(findings=0)),
      ('pmd-cli-count-confusion',lambda value:value['staticRaw']['pmd'].update(actualExit=2)),
      ('spotbugs-not-zero',lambda value:value['staticRaw']['spotbugs'].update(findings=1)),
      ('union',lambda value:value.update(coverageUnion=True))):
        changed=copy.deepcopy(current); mutate(changed)
        try: reviewed(changed,SOURCE,18,1,{PREFIX},review)
        except (ValueError,KeyError): rejected.append(name)
        else: raise AssertionError('bad current post accepted')
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    old=copy.deepcopy(proof['priorOwners']['sourceRows']); assert len(old)==246
    assert all(previous_owner.canonical(row['path'],logical)==owner.canonical(row['path'],logical) for row in old)
    for path in (MAIN,UNIT):
        assert path not in logical and previous_owner.canonical(path,logical)['ownershipStatus']=='UNKNOWN'
        resolved=owner.canonical(path,logical)
        assert resolved['canonicalOwner']==resolved['canonicalCostOwner']=='WBS-P018-05'
        assert resolved['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
        synthetic=dict(logical); synthetic[path]=dict(path=path,owner='WBS-F03',costOwner='WBS-F03')
        assert owner.canonical(path,synthetic)['canonicalOwner']=='WBS-F03'
    unknown=MAIN.replace('ApiStopBudget.java','ApiStopBudgetExtra.java')
    assert owner.canonical(unknown,logical)['ownershipStatus']=='UNKNOWN'
    rows=old+[dict(path=MAIN),dict(path=UNIT)]; joined=[]
    for row in rows:
        path=row['path']; raw=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-05')
        resolved=owner.join_rows([raw],logical,hashes,'WBS-P018-05')
        owner.validate(resolved,[raw],logical,hashes,'WBS-P018-05')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',
          priorObservationPreserved=True,oldSourcePtTransferred=False); joined.extend(resolved)
    assert len(joined)==len({row['path'] for row in joined})==248 and all(row['canonicalOwner'] for row in joined)
    for name,mutate in (
      ('new-path-wrong-owner',lambda values:values[-1].update(canonicalOwner='WBS-P018-09')),
      ('new-path-wrong-cost-owner',lambda values:values[-1].update(canonicalCostOwner='WBS-P018-09')),
      ('new-path-old-pt-inferred',lambda values:values[-1].update(currentSourcePtQualificationInferred=True))):
        changed=copy.deepcopy(joined); mutate(changed)
        raw=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in joined]
        # Compare only resolver fields: trace annotations are not part of the canonical resolver.
        fields=set(owner.join_rows([raw[-1]],logical,hashes,'WBS-P018-05')[0])
        tested=[{key:row[key] for key in fields} for row in changed]
        try: owner.validate(tested,raw,logical,hashes,'WBS-P018-05')
        except ValueError: rejected.append(name)
        else: raise AssertionError('false ownership accepted')
    pom=(host.ROOT/'pom.xml').read_text()
    assert '-Xep:NullAway:ERROR' in pom and 'NullAway:AnnotatedPackages=dev.codex.schubert.nk' in pom
    marker=snapshot/'src/schubert-nk-api/target/classes/dev/codex/schubert/nk/api/bootstrap/package-info.class'
    assert not marker.exists() and not (host.ROOT/MAIN).parent.joinpath('package-info.java').exists()
    assert set(current['physicalClasses'])=={PREFIX+'.class'} and current['customExclusionsAdded'] is False
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir(); steps.SLOT=SLOT; reader=SLOT/'reader'; reader.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(reader),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(reader),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1843 and len(analysis['rules'])==5 and not analysis['findings'] and all(value==0 for value in analysis['rules'].values())
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,
      allPhysicalClassCount=1843,physicalClasses=physical,addedPhysical=sorted(added),changedPhysical=[],previousPhysicalUnchanged=1842,
      sourceRows=joined,sourceCount=248,canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),
      newOwnerBasis='Original485 ApiProcessLifetime owner P01805 plus SS342 API60 stop responsibility; exact new Main/Test paths only; prior246 canonical mappings unchanged',
      ownerResolverHashes=dict(previous=host.sha(Path(previous_owner.__file__)),current=host.sha(Path(owner.__file__))),
      original246CanonicalMappingsPreserved=True,syntheticBaselinePrecedenceChecked=True,unregisteredBootstrapPathRemainsUnknown=True,
      currentTests=18,currentSuites=1,newTests=18,necessaryRegression=0,currentCounters=current['counters'],metadataCounterexamples=rejected,
      compilerNullAwayAnnotatedPackages='dev.codex.schubert.nk',namespaceMetadataClassActuallyAbsent=True,noExecutableClassExcluded=True,
      architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,
      coverageUnion=False,actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,allMain=1843,owners=248,newTests=18,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
