"""Same-source pure readiness evidence and exact Test owner; never native admission acceptance."""
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import trace_owner_join_api_fatal as previous_owner
import trace_owner_join_api_readiness as owner
from host_tool_invocation import capture, verify

host=base.host
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
OUT=host.BASE/'PG9288-api-pure-readiness-trace-v1'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiProcessMain'

def assess(value):
    assert value['source']==SOURCE and value['actualExit']==0 and value['actualTests']==3 and value['suites']==1
    assert value['newTestIds']==0 and value['necessaryRegression']==3
    assert value['failures']==value['errors']==value['skipped']==0
    names={PREFIX,PREFIX+'$Startup',PREFIX+'$ConfigurationLoad'}
    assert set(value['executableClasses'])==names
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert value[field] is False
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for name,row in value['executableClasses'].items():
        assert row['recordStatus']==('CURRENT_RECORD' if name==PREFIX else 'DECLARED_INTERFACE_NO_EXECUTABLE_CODE')
        assert set(row['counters'])==set(totals)
        for kind,count in row['counters'].items():
            assert set(count)=={'missed','covered'} and all(type(v) is int and v>=0 for v in count.values())
            if name!=PREFIX: assert not any(count.values())
            for key in count: totals[kind][key]+=count[key]
    assert totals==value['wholeSourceUnitCounters']==dict(LINE=dict(covered=8,missed=168),
      METHOD=dict(covered=4,missed=30),CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=10,missed=8))

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    pins={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'host':('PG9284-api-pure-readiness-host-v1/manifest.json','08188fea15ae032bf77ec0e34e571b6a63eb273e4222ad9f5b8eb4f722d8f95f'),
      'measure':('PG9286-api-pure-readiness-measure-v1/manifest.json','722dfd2319f371d57c92717f8dd240e46ace92eb2bf0079d68bc48a75438375c'),
      'sameSourcePhysical':('PG9252-web-life-lock-trace-v1/manifest.json','70f008f4256751e5bf4ecc0baa9e398dc715643cbbff8eb1380927fbfb7d49b6'),
      'priorOwners':('PG9276-api-fatal-callback-trace-v2/manifest.json','05bb33c3c4a35cd04945ffa0baf18c07166f6a97a3a7488b8d8cc96c4007906e'),
      'mainStaticByteWitness':('PG9197-api-main-observation-static-v1/manifest.json','aeddd461450c49be5bcfe78b84cb4bad9bd8b6442fbf8fdda56a211c46e5924e')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,measure,run,physical_proof,prior=proof['normal'],proof['measure'],proof['host'],proof['sameSourcePhysical'],proof['priorOwners']
    assess(measure)
    assert normal['source']==run['source']==physical_proof['source']==prior['source']==SOURCE
    assert normal['actualExit']==run['actualExit']==physical_proof['actualExit']==prior['actualExit']==0
    assert run['begin']['compileManifestSha256']==pins['normal'][1]
    assert len(run['cases'])==3 and all(row['result']=='PASS' and not row['nonPass'] for row in run['cases'])
    assert {row['name'] for row in run['cases']}=={
      'health001LiteralTruthTablesAndShortCircuitOrder','health002EveryCallReadsCurrentStateWithoutLatchingSuccess',
      'health003NullAndExactFailureAreNeverConvertedToHealth'}
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9246-web-life-lock-six-compile-v1/snapshot'
    assert all(host.sha(host.ROOT/path)==host.sha(snapshot/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); assert len(physical)==1843 and physical==physical_proof['physicalClasses']
    for member,digest in measure['physicalClasses'].items(): assert physical['api:'+member]==digest
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    raw=proof['mainStaticByteWitness']; assert raw['actualExit']==1 and hashes[MAIN]==raw['sourceHashes'][MAIN]
    assert raw['static']['pmd']['findings']==2 and raw['static']['pmd']['receipt']['actualExit']==4
    for member,digest in raw['physicalClasses'].items(): assert physical['api:'+member]==digest
    assert not physical_proof['architecture']['result']['findings']
    assert all(v==0 for v in physical_proof['architecture']['result']['rules'].values())
    rejected=[]
    for name,mutate in (
      ('wrong-source',lambda v:v.update(source='0'*40)),
      ('whole100-invented',lambda v:v.update(requiredWholeClassFour100=True)),
      ('coverage-union',lambda v:v.update(coverageUnion=True)),
      ('interface-excluded',lambda v:v['executableClasses'].pop(PREFIX+'$Startup')),
      ('missed-zeroed',lambda v:v['wholeSourceUnitCounters']['LINE'].update(missed=0)),
      ('old-hook-selected',lambda v:v.update(historicalHookOrTermCasesSelected=True))):
        changed=copy.deepcopy(measure); mutate(changed)
        try: assess(changed)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false Main qualification')
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    old_rows=prior['sourceRows']; assert len(old_rows)==255 and owner.TEST not in {row['path'] for row in old_rows}
    assert all(host.sha(host.ROOT/row['path'])==row['sha256'] for row in old_rows)
    assert all(previous_owner.canonical(row['path'],logical)==owner.canonical(row['path'],logical) for row in old_rows)
    assert previous_owner.canonical(owner.TEST,logical)['canonicalOwner'] is None
    assert owner.canonical(owner.TEST,logical)['canonicalOwner']=='WBS-P018-05'
    assert owner.canonical(owner.TEST.replace('PredicateTest','PredicateTestForeign'),logical)['canonicalOwner'] is None
    joined=[]
    for row in old_rows+[dict(path=owner.TEST,legacyReportedOwner='WBS-P018-05')]:
        path=row['path']; item=dict(path=path,sha256=hashes[path],owner=row['legacyReportedOwner'])
        resolved=owner.join_rows([item],logical,hashes,'WBS-P018-05'); owner.validate(resolved,[item],logical,hashes,'WBS-P018-05')
        resolved[0].update(changedInThisSource=False,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',oldSourcePtTransferred=False); joined.extend(resolved)
    guard_input=[dict(path=owner.TEST,sha256=hashes[owner.TEST],owner='WBS-P018-05')]
    positive=owner.join_rows(guard_input,logical,hashes,'WBS-P018-05')
    owner.validate(positive,guard_input,logical,hashes,'WBS-P018-05')
    false=copy.deepcopy(positive); false[0]['canonicalCostOwner']='WBS-P018-06'
    assert {key for key in positive[0] if positive[0][key]!=false[0][key]}=={'canonicalCostOwner'}
    try: owner.validate(false,guard_input,logical,hashes,'WBS-P018-05')
    except ValueError: rejected.append('wrong-canonical-cost-owner')
    else: raise AssertionError('wrong cost owner accepted')
    assert len(joined)==len({row['path'] for row in joined})==256
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,allPhysicalClassCount=1843,all1843MainBytesUnchanged=True,
      physicalInventoryReference=pins['sameSourcePhysical'],sourceRows=joined,sourceCount=256,
      previous255CanonicalMappingsAndSourceHashesPreserved=True,costGuardPositiveShapeValidated=True,costGuardOnlyChangedField='canonicalCostOwner',
      newTestIds=0,currentTests=3,currentSuites=1,necessaryRegression=3,newMain=0,
      declaredInterfacesNaturallyIncluded=True,wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],
      requiredWholeClassFour100=False,programPtComplete=False,
      staticWitnessScope='EXACT_MAIN_BYTES_ONLY_NOT_OLD_COVERAGE_OR_CURRENT_FULL_QUALITY_PASS',
      metadataCounterexamples=rejected,normalCompileReplayed=False,staticReplayed=False,architectureReplayed=False,
      oldSourcePtTransferred=False,coverageUnion=False,productTestsExecutedByTrace=0,actualMainNativePt='UNRUN_HOLD',
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,currentTests=3,newTestIds=0,owners=256,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
