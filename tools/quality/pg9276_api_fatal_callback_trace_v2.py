"""Compact same-source reference: no full inventories copied, no build/static/architecture replay."""
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import trace_owner_join_api_web_life as previous_owner
import trace_owner_join_api_fatal as owner
from host_tool_invocation import capture, verify

host=base.host
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
OUT=host.BASE/'PG9276-api-fatal-callback-trace-v2'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.java'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime'

def assess(value):
    assert value['source']==SOURCE and value['actualExit']==0 and value['actualTests']==2 and value['suites']==1
    assert value['newTestIds']==0 and value['necessaryRegression']==2
    assert value['failures']==value['errors']==value['skipped']==0
    assert set(value['executableClasses'])=={PREFIX,PREFIX+'$1'}
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert value[field] is False
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for row in value['executableClasses'].values():
        assert set(row['counters'])==set(totals)
        for kind,count in row['counters'].items():
            assert set(count)=={'missed','covered'} and all(type(v) is int and v>=0 for v in count.values())
            for key in count: totals[kind][key]+=count[key]
    assert totals==value['wholeSourceUnitCounters']==dict(LINE=dict(covered=27,missed=41),
      METHOD=dict(covered=9,missed=10),CLASS=dict(covered=1,missed=1),BRANCH=dict(covered=4,missed=10))
    inner=value['executableClasses'][PREFIX+'$1']['counters']
    assert inner==dict(LINE=dict(covered=0,missed=7),METHOD=dict(covered=0,missed=3),
      CLASS=dict(covered=0,missed=1),BRANCH=dict(covered=0,missed=0))
    assert value['executableClasses'][PREFIX]['recordStatus']=='CURRENT_RECORD'
    assert value['executableClasses'][PREFIX+'$1']['recordStatus']=='UNEXECUTED_NO_RECORD_NOT_QUALIFIED'

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    pins={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'host':('PG9272-api-fatal-callback-host-v1/manifest.json','25a1cf61471062d89485941c96da5fdb550155e9d40a4f6395eb501f836e04ea'),
      'measure':('PG9274-api-fatal-callback-measure-v1/manifest.json','4862a4949538a46497b3f2cabbb53e98e7a95922d65b3f873c1dcaf8b0ead008'),
      'sameSourceTrace':('PG9252-web-life-lock-trace-v1/manifest.json','70f008f4256751e5bf4ecc0baa9e398dc715643cbbff8eb1380927fbfb7d49b6'),
      'apiStaticByteWitness':('PG9235-api-web-life-remedy-static-v1/manifest.json','0c67b6d9c9e74f3b7276bd716f1741957c704cb3f599668f471608fbde9477bc')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,measure,run,prior=proof['normal'],proof['measure'],proof['host'],proof['sameSourceTrace']
    assess(measure)
    assert normal['source']==run['source']==prior['source']==SOURCE
    assert normal['actualExit']==run['actualExit']==prior['actualExit']==0
    assert run['begin']['compileManifestSha256']==pins['normal'][1]
    assert len(run['cases'])==2 and all(row['result']=='PASS' and not row['nonPass'] for row in run['cases'])
    assert set(row['name'] for row in run['cases'])=={
      'fatalBinding001CommittedEventStopsOwnerAndAwaitRemainsSanitizedNonSuccess','fatalBinding002CallbackRemainsBoundToItsOwnerAndNeverReadsFailurePayload'}
    assert all(row['actualExit']==0 and row['timedOut'] is False for row in run['stages'])
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9246-web-life-lock-six-compile-v1/snapshot'
    assert all(host.sha(host.ROOT/path)==host.sha(snapshot/path)==digest for path,digest in hashes.items())
    physical=base.inventory(normal); assert len(physical)==1843 and physical==prior['physicalClasses']
    for member,digest in measure['physicalClasses'].items(): assert physical['api:'+member]==digest
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    assert prior['sourceCount']==254 and all(host.sha(host.ROOT/row['path'])==row['sha256'] for row in prior['sourceRows'])
    static=proof['apiStaticByteWitness']
    assert hashes[API]==static['sourceHashes'][API]
    for member,digest in static['physicalClasses'].items():
        if '/api/' in member: assert physical['api:'+member]==digest
    api_rows=[row for row in static['static']['pmd']['rawFindings'] if row['class']=='ApiProcessLifetime']
    assert len(api_rows)==7 and all(row['rule'] in ('DoNotUseThreads','CompareObjectsWithEquals') for row in api_rows)
    assert not prior['architecture']['result']['findings'] and all(v==0 for v in prior['architecture']['result']['rules'].values())
    rejected=[]
    for name,mutate in (
      ('wrong-source',lambda v:v.update(source='0'*40)),
      ('whole100-invented',lambda v:v.update(requiredWholeClassFour100=True)),
      ('old-record-union',lambda v:v.update(coverageUnion=True)),
      ('inner-unexecuted-normalized',lambda v:v['executableClasses'][PREFIX+'$1'].update(recordStatus='CURRENT_RECORD')),
      ('missed-zeroed',lambda v:v['wholeSourceUnitCounters']['LINE'].update(missed=0)),
      ('inner-class-missed-hidden',lambda v:v['executableClasses'][PREFIX+'$1']['counters']['CLASS'].update(missed=0)),
      ('old-hook-selected',lambda v:v.update(historicalHookOrTermCasesSelected=True))):
        changed=copy.deepcopy(measure); mutate(changed)
        try: assess(changed)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false whole-program acceptance')
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    old_rows=prior['sourceRows']; assert len(old_rows)==254 and owner.TEST not in {row['path'] for row in old_rows}
    assert all(previous_owner.canonical(row['path'],logical)==owner.canonical(row['path'],logical) for row in old_rows)
    assert previous_owner.canonical(owner.TEST,logical)['canonicalOwner'] is None
    assert owner.canonical(owner.TEST,logical)['canonicalOwner']=='WBS-P018-05'
    assert owner.canonical(owner.TEST.replace('BindingTest','BindingTestForeign'),logical)['canonicalOwner'] is None
    joined=[]
    for row in old_rows+[dict(path=owner.TEST,legacyReportedOwner='WBS-P018-05')]:
        path=row['path']; item=dict(path=path,sha256=hashes[path],owner=row['legacyReportedOwner'])
        resolved=owner.join_rows([item],logical,hashes,'WBS-P018-05')
        owner.validate(resolved,[item],logical,hashes,'WBS-P018-05')
        resolved[0].update(changedInThisSource=False,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',oldSourcePtTransferred=False)
        joined.extend(resolved)
    guard_input=[dict(path=owner.TEST,sha256=hashes[owner.TEST],owner='WBS-P018-05')]
    positive=owner.join_rows(guard_input,logical,hashes,'WBS-P018-05')
    owner.validate(positive,guard_input,logical,hashes,'WBS-P018-05')
    false=copy.deepcopy(positive); false[0]['canonicalCostOwner']='WBS-P018-06'
    assert {key for key in positive[0] if false[0][key]!=positive[0][key]}=={'canonicalCostOwner'}
    try: owner.validate(false,guard_input,logical,hashes,'WBS-P018-05')
    except ValueError: rejected.append('wrong-canonical-cost-owner')
    else: raise AssertionError('wrong callback cost owner accepted')
    assert len(joined)==255 and len({row['path'] for row in joined})==255
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,allPhysicalClassCount=1843,all1843MainBytesUnchanged=True,
      physicalInventoryReference=pins['sameSourceTrace'],sourceRows=joined,sourceCount=255,
      costGuardPositiveShapeValidated=True,costGuardOnlyChangedField='canonicalCostOwner',previous254CanonicalMappingsAndSourceHashesPreserved=True,newTestIds=0,currentTests=2,currentSuites=1,necessaryRegression=2,newMain=0,
      callbackGuardInnerUnexecutedNotQualified=True,
      wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],requiredWholeClassFour100=False,programPtComplete=False,
      apiStaticWitnessScope='SOURCE_AND_PHYSICAL_BYTES_ONLY_NOT_OLD_COVERAGE_OR_CURRENT_FULL_QUALITY_PASS',
      apiHistoricalRawPmd=7,metadataCounterexamples=rejected,normalCompileReplayed=False,staticReplayed=False,
      architectureReplayed=False,oldSourcePtTransferred=False,coverageUnion=False,
      productTestsExecutedByTrace=0,actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,currentTests=2,newTestIds=0,innerUnexecuted=True,owners=255,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
