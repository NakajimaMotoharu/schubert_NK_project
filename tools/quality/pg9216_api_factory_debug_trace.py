"""New method-only fixture evidence; unchanged Main byte comparison is not old PT transfer."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import pg9188_api_lifetime_budget_trace as legacy
import trace_owner_join_api_main as owner
from host_tool_invocation import capture, verify

host=base.host
SOURCE='3641d0f49e6b33fe64de718703f134406dfddb30'
BEFORE='9f7a3215621dca09184ea24d0ba824b3a002b329'
OUT=host.BASE/'PG9216-api-factory-debug-trace-v1'
TEST=owner.TEST
BRIDGE='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiFactoryObservationFixture.java'
PREFIX='dev/codex/schubert/nk/api/bootstrap/ApiProcessMain'

def assess(measure,run):
    assert measure['source']==run['source']==SOURCE and measure['actualExit']==run['actualExit']==0
    assert measure['actualTests']==1 and measure['suites']==1 and measure['exactSelectedCaseIds']==['apiObsBoot009']
    assert len(run['cases'])==1 and run['cases'][0]['name']=='apiObsBoot009' and run['cases'][0]['result']=='PASS'
    assert not run['cases'][0]['nonPass']
    for field in ('requiredWholeClassFour100','coverageUnion','exclusionsAdded','coverageRequirementRelaxed',
                  'historicalHookOrTermCasesSelected','programPtComplete','whole451Accepted','formalUpdated'):
        assert measure[field] is False
    assert measure['failures']==measure['errors']==measure['skipped']==0
    names={PREFIX,PREFIX+'$Startup',PREFIX+'$ConfigurationLoad'}
    assert set(measure['executableClasses'])==names
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for name,row in measure['executableClasses'].items():
        assert row['recordStatus']==('CURRENT_RECORD' if name==PREFIX else 'DECLARED_INTERFACE_NO_EXECUTABLE_CODE')
        assert set(row['counters'])==set(totals)
        for kind,count in row['counters'].items():
            assert set(count)=={'missed','covered'} and all(type(v) is int and v>=0 for v in count.values())
            if name!=PREFIX: assert not any(count.values())
            for key in count: totals[kind][key]+=count[key]
    assert totals==measure['wholeSourceUnitCounters'] and any(row['missed']>0 for row in totals.values())

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    pins={
      'normal':('PG9210-api-factory-debug-six-compile-v1/manifest.json','80b8d4f5f4e16723b5871771fcd3bd03bd068e2a59d17cbf1e8d6e8486f3a39b'),
      'host':('PG9212-api-factory-debug-host-v1/manifest.json','4cd4eb6f77314c8a42096078100eef9b989fd2c5930948448b4b773326448f1a'),
      'measure':('PG9214-api-factory-debug-measure-v2/manifest.json','f506719d825662d5e88b233a68c859a3ae69da983334df83166143980e4ed237'),
      'previous':('PG9202-api-main-observation-trace-v1/manifest.json','646a8d8e05a439b85c56b80f323529a8366f2adbd897ed8b2849a0fd731c696d')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,run,measure,previous=proof['normal'],proof['host'],proof['measure'],proof['previous']
    assess(measure,run); assert normal['actualExit']==0 and normal['source']==SOURCE
    assert measure['wrongOldSessionRejected'] is True
    assert measure['wrongOldSessionReceipt']['actualExit']==1 and measure['wrongOldSessionReceipt']['timedOut'] is False
    assert run['begin']['compileManifestSha256']==pins['normal'][1]
    assert all(row['actualExit']==0 and row['timedOut'] is False for row in run['stages'])
    hashes=normal['begin']['inputHashes']; snapshot=host.W/'pg9210-api-factory-debug-six-compile-v1/snapshot'
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    assert all(host.sha(Path(path))==digest for path,digest in run['begin']['testSourceHashes'].items())
    physical=base.inventory(normal)
    assert len(physical)==1843 and physical==previous['physicalClasses']
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={TEST,BRIDGE}
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    old=subprocess.check_output(['git','show',BEFORE+':'+TEST],cwd=host.ROOT).decode()
    current=(host.ROOT/TEST).read_text(); prior_cases=legacy.cases(old); current_cases=legacy.cases(current)
    assert len(prior_cases)==8 and len(current_cases)==9
    assert all(current_cases[name]==body for name,body in prior_cases.items())
    assert set(current_cases)-set(prior_cases)=={'apiObsBoot009'}
    assert all(token not in current for token in ('new ApiProcessMain(','.main(','.run(','.install(','HookDriver','ProcessBuilder'))
    bridge=(host.ROOT/BRIDGE).read_text()
    assert all(token not in bridge for token in ('super.getConnection','new HikariConfig','DriverManager','System.setProperty'))
    assert 'System.getProperty("hikaricp.configurationFile")' in bridge
    rejected=[]
    for name,scope,mutate in (
      ('wrong-source','measure',lambda v:v.update(source=BEFORE)),
      ('whole100-invented','measure',lambda v:v.update(requiredWholeClassFour100=True)),
      ('old-record-union','measure',lambda v:v.update(coverageUnion=True)),
      ('metadata-interface-excluded','measure',lambda v:v['executableClasses'].pop(PREFIX+'$Startup')),
      ('old-method-selected','run',lambda v:v['cases'][0].update(name='apiObsBoot001')),
      ('failure-hidden','run',lambda v:v['cases'][0].update(nonPass=['failure']))):
        values=dict(measure=copy.deepcopy(measure),run=copy.deepcopy(run)); mutate(values[scope])
        try: assess(**values)
        except (AssertionError,ValueError,KeyError,TypeError): rejected.append(name)
        else: raise AssertionError('false new fixture qualification accepted')
    inventory=json.loads((host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    prior=previous['sourceRows']; assert len(prior)==251 and BRIDGE not in {row['path'] for row in prior}
    joined=[]
    for row in prior+[dict(path=BRIDGE)]:
        path=row['path']; item=dict(path=path,sha256=hashes[path],owner=row.get('legacyReportedOwner') or 'WBS-P018-05')
        resolved=owner.join_rows([item],logical,hashes,'WBS-P018-05')
        owner.validate(resolved,[item],logical,hashes,'WBS-P018-05')
        resolved[0].update(changedInThisSource=path in delta,observationKind='CURRENT_HASH_AND_OWNER_NOT_WHOLE_PT',oldSourcePtTransferred=False)
        joined.extend(resolved)
    assert len(joined)==252 and owner.canonical(BRIDGE,logical)['canonicalOwner']=='WBS-P018-09'
    assert all(owner.canonical(row['path'],logical)=={key:row[key] for key in ('canonicalOwner','canonicalCostOwner','ownershipStatus','basis')} for row in prior)
    architecture=previous['architecture']
    assert architecture['result']['physical']==1843 and not architecture['result']['findings']
    assert all(value==0 for value in architecture['result']['rules'].values())
    failed=host.W/'pg9214-api-factory-debug-measure-v1'
    old_tool=host.ROOT/'tools/quality/pg9214_api_factory_debug_measure.py'
    assert host.sha(old_tool)=='e59924725e064ed9553fe0c7ad96f77d77b1f276dc6eb2dbcf3546f57c741d1e'
    old_exit=json.loads((failed/'measure-report-exit.safe.json').read_bytes())
    assert old_exit['actualExit']==1 and old_exit['timedOut'] is False
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,allPhysicalClassCount=1843,physicalClasses=physical,
      previous1843MainBytesUnchanged=True,changedPhysical=[],sourceRows=joined,sourceCount=252,
      canonicalOwnerCounts=dict(Counter(row['canonicalOwner'] for row in joined)),previous251CanonicalMappingsPreserved=True,
      newTests=1,currentTests=1,currentSuites=1,newMain=0,legacy8TestBodiesUnchanged=True,
      wholeSourceUnitCounters=measure['wholeSourceUnitCounters'],requiredWholeClassFour100=False,programPtComplete=False,
      priorArchitectureReusedForExactSame1843Bytes=True,priorArchitectureManifestSha256=pins['previous'][1],
      architectureReexecuted=False,priorStaticApplicability='UNCHANGED_MAIN_BYTES_ONLY_NOT_CURRENT_FULL_QUALITY_PASS',
      metadataCounterexamples=rejected,oldSourcePtTransferred=False,coverageUnion=False,
      failedV1ReaderReceipt=old_exit,failedV1ReaderSourceSha256=host.sha(old_tool),
      failedV1ReaderStderrSha256=host.sha(failed/'measure-report.stderr.log'),bug1741Retest='CURRENT_SESSION_ACCEPTED_OLD_SESSION_REJECTED_NO_PRODUCT_REPLAY',
      productTestsExecutedByTrace=0,actualMainNativePt='UNRUN_HOLD',whole451Accepted=False,
      formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,allMain=1843,owners=252,newTests=1,metadataNegatives=len(rejected))))

if __name__=='__main__':main()
