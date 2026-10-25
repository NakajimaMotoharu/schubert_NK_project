"""Compact same-source reference: no full inventories copied, no build/static/architecture replay."""
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
from host_tool_invocation import capture, verify

host=base.host
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
OUT=host.BASE/'PG9264-api-ordinary-guard-trace-v1'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.java'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime'

def assess(value):
    assert value['source']==SOURCE and value['actualExit']==0 and value['actualTests']==2 and value['suites']==1
    assert value['newTestIds']==0 and value['necessaryRegression']==2 and value['newMain']==0
    assert value['failures']==value['errors']==value['skipped']==0
    assert set(value['executableClasses'])=={PREFIX,PREFIX+'$1'}
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert value[field] is False
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for row in value['executableClasses'].values():
        assert row['recordStatus']=='CURRENT_RECORD' and set(row['counters'])==set(totals)
        for kind,count in row['counters'].items():
            assert set(count)=={'missed','covered'} and all(type(v) is int and v>=0 for v in count.values())
            for key in count: totals[kind][key]+=count[key]
    assert totals==value['wholeSourceUnitCounters']==dict(LINE=dict(covered=51,missed=17),
      METHOD=dict(covered=15,missed=4),CLASS=dict(covered=2,missed=0),BRANCH=dict(covered=10,missed=4))
    inner=value['executableClasses'][PREFIX+'$1']['counters']
    assert inner==dict(LINE=dict(covered=7,missed=0),METHOD=dict(covered=3,missed=0),
      CLASS=dict(covered=1,missed=0),BRANCH=dict(covered=0,missed=0))

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    pins={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'host':('PG9260-api-ordinary-guard-host-v1/manifest.json','e75d4ba99d0d4f91c907137a29d7ef483e9331984f599e341d7bb5bbe005af19'),
      'measure':('PG9262-api-ordinary-guard-measure-v1/manifest.json','d10a3d37c2c05bb431cf1ca988b8af02dba11400a2d1de9d127fa57ca972d095'),
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
      'ready004BorrowedDelegatesStopGuardAndActualDeliveryPreserved','ready005HealthFailureInterruptedAndNormalStopDistinct'}
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
      ('inner-unexecuted-normalized',lambda v:v['executableClasses'][PREFIX+'$1'].update(recordStatus='UNEXECUTED_NO_RECORD_NOT_QUALIFIED')),
      ('missed-zeroed',lambda v:v['wholeSourceUnitCounters']['LINE'].update(missed=0)),
      ('new-main-invented',lambda v:v.update(newMain=1)),
      ('old-hook-selected',lambda v:v.update(historicalHookOrTermCasesSelected=True))):
        changed=copy.deepcopy(measure); mutate(changed)
        try: assess(changed)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false whole-program acceptance')
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,allPhysicalClassCount=1843,all1843MainBytesUnchanged=True,
      physicalInventoryReference=pins['sameSourceTrace'],sourceRowsReference=pins['sameSourceTrace'],sourceCount=254,
      all254CanonicalMappingsAndSourceHashesPreserved=True,newTestIds=0,currentTests=2,currentSuites=1,necessaryRegression=2,newMain=0,
      qualifiedExistingInnerClass=measure['qualifiedExistingInnerClass'],
      wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],requiredWholeClassFour100=False,programPtComplete=False,
      apiStaticWitnessScope='SOURCE_AND_PHYSICAL_BYTES_ONLY_NOT_OLD_COVERAGE_OR_CURRENT_FULL_QUALITY_PASS',
      apiHistoricalRawPmd=7,metadataCounterexamples=rejected,normalCompileReplayed=False,staticReplayed=False,
      architectureReplayed=False,oldSourcePtTransferred=False,coverageUnion=False,
      productTestsExecutedByTrace=0,actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,currentTests=2,newTestIds=0,existingInnerAllMissedZero=True,owners=254,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
