from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from zipfile import ZipFile
import json,os,subprocess

root=Path.cwd()
work=root.parent/'pgpt-runs/PG379'
run=work/'PG43424-current-poller-boundaries-v2'
src=Path('evidence/01_PT/018_NK-OPS-001/evidence')
def proof(n):return next(src.glob(f'PG{n}-*/manifest.json'))
def j(p):return json.loads(p.read_bytes())
def digest(data):return sha256(data).hexdigest()
def pin(p):return dict(path=str(p),sha256=digest(p.read_bytes()))
def put(p,o):
    with p.open('x') as f:f.write(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def git(*args):return subprocess.check_output(['git',*args])
h=git('rev-parse','HEAD').decode().strip()
assert h.startswith('087469471c')
prior=j(proof(42598))
previous=j(proof(43420))
assert prior['compileExit']==0 and prior['ordinaryTestsPassed']==12 and previous['actualExit']==0
old=Path(prior['typedInput']['path'])
assert pin(old)==prior['typedInput']
fixture_dir=old.parent/'fixture'
p='dev/codex/schubert/nk/batch/monitoring/'
names=('MonitoringPollerTest','MonitoringObservationClockTest','FilesystemHealthObservationTest')
slices=[v for v in prior['targetedFixtures'] if any(v['path'].endswith(n+'.java') for n in names)]
assert len(slices)==3
for item in slices:
    sp=Path(item['path'])
    assert digest(git('show',f'{h}:{sp}'))==digest(sp.read_bytes())==item['sha256']
current=Path(previous['candidateBatchArtifact']['path'])
assert pin(current)==previous['candidateBatchArtifact']
paths=prior['allowedBorrowedProductClosure']
assert len(paths)==19
replaced={k for k,v in paths.items() if previous['regularArchiveScope'].get(k) not in (None,v['sha256'])}
assert replaced=={p+'ContinuousConditionWindow.class',p+'TimedFilesystemMonitor.class'}
include=j(proof(43052))
tool_names={Path(r['path']).name:r for r in include['tools'] if Path(r['path']).is_absolute()}
def tools(*names):
    result=[]
    for n in names:
        row=tool_names[n];q=Path(row['path']);assert pin(q)==row;result.append(q)
    return result
junit,jspec,agent=tools('junit-platform-console-standalone-1.13.4.jar','jspecify-1.0.1.jar','org.jacoco.agent-0.8.15-runtime.jar')
sdk=tools('org.jacoco.core-0.8.15.jar','asm-9.10.1.jar','asm-commons-9.10.1.jar','asm-tree-9.10.1.jar')
home=root.parent/'toolchain/jdk-25.0.4/bin'
with ZipFile(current) as z:
    entries={k:z.read(k) for k in paths}
assert all(digest(entries[k])==(previous['regularArchiveScope'][k] if k in replaced else v['sha256']) for k,v in paths.items())
run.mkdir()
production,fixtures,xml=(run/x for x in ('production','tests','xml'))
for path in (production,fixtures,xml):path.mkdir()
for k,v in entries.items():
    f=production/k
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_bytes(v)
fixture_family_members={
 'MonitoringPollerTest': {'MonitoringPollerTest.class'},
 'MonitoringObservationClockTest': {'MonitoringObservationClockTest.class','MonitoringObservationClockTest$FixtureClock.class','MonitoringObservationClockTest$UnformattableFailure.class'},
 'FilesystemHealthObservationTest': {'FilesystemHealthObservationTest.class','FilesystemHealthObservationTest$FixtureStore.class','FilesystemHealthObservationTest$UnformattableIOException.class'},
}
assert names==tuple(fixture_family_members)
compiled={}
for name in names:
    src_dir=fixture_dir/p
    original=[src_dir/(name+'.class'),*src_dir.glob(name+'$*.class')]
    assert {f.name for f in original}==fixture_family_members[name]
    for f in original:
        target=fixtures/p/f.name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(f.read_bytes())
        compiled[str(f.relative_to(fixture_dir))]=pin(f)
expected={
 'PT-OPS-POLL001':'poll001NormalFlagsContextAndResultHaveNoRetries',
 'PT-OPS-POLL003':'poll003BackwardsContextIsRejectedBeforeActionAndDoesNotInventGap',
 'PT-OPS-POLL004':'poll004ClockFailureHasNoActionAndCrossApiGapIsConsumed',
 'PT-OPS-POLL005':'poll005NullBoundariesDoNotCallOrChangeContinuity',
 'PT-OPS-POLL006':'poll006NullResultIsFailureAndDoesNotCommitLaterEpoch',
}
target_test=p.replace('/','.')+names[0]
coverage_target=p+'MonitoringPoller'
exec_file=run/'selected.exec'
def cp(*paths):return os.pathsep.join(map(str,paths))
unit=[home/'java',f'-javaagent:{agent}=destfile={exec_file},append=false,sessionid=PG43424-POLL5,includes={coverage_target.replace("/",".")}',
      f'-Xlog:class+init=info:file={run / "class-init.log"}','-Duser.language=ja','-Duser.timezone=Asia/Tokyo',
      '-Djunit.jupiter.extensions.autodetection.enabled=false','-jar',junit,'execute',
      '--class-path',cp(production,fixtures,jspec),*[v for method in expected.values() for v in ('--select-method',target_test+'#'+method)],
      '--reports-dir',xml,'--details','summary','--disable-banner','--fail-if-no-tests']
measure_bin=work/'PG43378-log-search-current-sixteen-v1/measurement'
analyse=[home/'java','-cp',cp(measure_bin,*sdk),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',
         '--strict-original-exec',exec_file,production/(coverage_target+'.class')]
argv={k:[str(x) for x in v] for k,v in dict(unit=unit,analyse=analyse).items()}
put(run/'begin.json',dict(source=h,productionCore=previous['productCore'],startedAtUTC=now(),
      referencedQualification=pin(proof(42598)),fixture_sources=slices,compiledFixture=compiled,expected=expected,
      currentBatch=pin(current),currentPhysical={k:digest(v) for k,v in entries.items()},coverageTarget=coverage_target,
      currentChangedAuxiliaries=sorted(replaced),testOutsideSelectionExcluded=True,
      originalFailedToolSetup=pin(proof(43424)),fixtureOnlyDependencyOfClock=sorted(fixture_family_members['FilesystemHealthObservationTest']),
      toolPins=[pin(x) for x in (junit,jspec,agent,*sdk)],
      rawAnalyserClasses=[pin(f) for f in sorted(measure_bin.rglob('UnfilteredCodeMeasurement*.class'))],
      commands=argv))
res={}
for mode,cmd in argv.items():
    with (run/f'{mode}.stdout').open('wb') as out,(run/f'{mode}.stderr').open('wb') as err:
        res[mode]=subprocess.run(cmd,cwd=root,stdout=out,stderr=err,timeout=60).returncode
    if res[mode]:break
put(run/'terminal.json',dict(source=h,terminalAtUTC=now(),results=res))
print(res)
if res.get('analyse')==0:
    print('\n'.join(line for line in (run/'analyse.stdout').read_text().splitlines() if line.startswith('CLASS\t')))
raise SystemExit(next(reversed(res.values())))
