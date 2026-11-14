"""BUG2877 local isolated real-filesystem negative tests; no remote phase, original asset or API receipt."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, stat, tempfile, time

r = Path.cwd()
source = r/'evidence/01_PT/018_NK-OPS-001/input/2564_haruka_common60_remote.py'
spec = importlib.util.spec_from_file_location('haruka_remote_tool_guard_test',source)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
results = []

def refuse(call, label):
    try:
        call()
    except (FileExistsError, ValueError):
        results.append(dict(id=label,expected='REFUSE',actual='REFUSE',result='PASS'))
        return
    raise AssertionError(label+' must refuse')

with tempfile.TemporaryDirectory(prefix='haruka-tool-local-fixture-only-') as temporary:
    root = Path(temporary)
    tool.RUN = root/'owned'
    tool.RUN.mkdir(mode=0o700)
    tool.BASE_TMP = root/'low'
    first = tool.establish_phase_tmp('prepare')
    assert first==root/'low-prepare'
    assert stat.S_IMODE(first.stat().st_mode)==0o700
    results.append(dict(id='TOOL-HARUKA-TMP01',expected='NEW_0700_PREPARE',actual='NEW_0700_PREPARE',result='PASS'))
    refuse(lambda: tool.establish_phase_tmp('prepare'),'TOOL-HARUKA-TMP02')
    # Independent simulation of the old phase directory being absent: next phase has its own name.
    first.rmdir()
    second = tool.establish_phase_tmp('run')
    assert second==root/'low-run' and second.is_dir() and not first.exists()
    results.append(dict(id='TOOL-HARUKA-TMP03',expected='NEW_RUN_WITH_OLD_PREPARE_ABSENT',actual='NEW_RUN_WITH_OLD_PREPARE_ABSENT',result='PASS'))
    refuse(lambda: tool.establish_phase_tmp('unknown'),'TOOL-HARUKA-TMP04')
    tool.BASE_TMP = root/'file-conflict'
    (root/'file-conflict-prepare').write_text('KEEP')
    refuse(lambda: tool.establish_phase_tmp('prepare'),'TOOL-HARUKA-TMP05')
    assert (root/'file-conflict-prepare').read_text()=='KEEP'
    tool.BASE_TMP = root/'link-conflict'
    target = root/'synthetic-unrelated-file'
    target.write_text('KEEP')
    (root/'link-conflict-prepare').symlink_to(target)
    refuse(lambda: tool.establish_phase_tmp('prepare'),'TOOL-HARUKA-TMP06')
    assert target.read_text()=='KEEP' and (root/'link-conflict-prepare').is_symlink()
    # Project artifacts are excluded while similarly named public dev dependencies remain copyable.
    tool.OLD_CACHE = root/'public-cache'
    keep = tool.OLD_CACHE/'dev/failsafe/vendor/item.jar'
    keep.parent.mkdir(parents=True)
    keep.write_bytes(b'PUBLIC_VENDOR_FIXTURE')
    excluded = tool.OLD_CACHE/'dev/codex/schubert/own-project/item.bin'
    excluded.parent.mkdir(parents=True)
    excluded.write_bytes(b'PROJECT_FIXTURE_NOT_TO_COPY')
    (tool.RUN/'owner.json').write_text(json.dumps(dict(deadlineMonotonic=time.monotonic()+60)))
    assert tool.copy_public_cache()==1
    assert (tool.RUN/'repository/dev/failsafe/vendor/item.jar').read_bytes()==b'PUBLIC_VENDOR_FIXTURE'
    assert not (tool.RUN/'repository/dev/codex/schubert').exists()
    results.append(dict(id='TOOL-HARUKA-CACHE01',expected='PUBLIC_VENDOR_ONLY_PROJECT_ABSENT',actual='PUBLIC_VENDOR_ONLY_PROJECT_ABSENT',result='PASS'))
    refuse(tool.copy_public_cache,'TOOL-HARUKA-CACHE02')

e = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG30702-haruka-phase-tmp-and-private-cache-local-tool-checks-v1'
assert not e.exists()
e.mkdir()
m = dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         bug='BUG-2877',horizontal='YKT-2411',localToolAssertions=len(results),cases=results,
         sourcePath=str(source.relative_to(r)),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
         independentExpectations='literal path/mode0700/KEEP/vendor fixture bytes; full method under test, no extracted surrogate',
         oldFailedRunUntouched=True,remoteConnections=0,productTestsExecuted=0,
         actualApiCalls=0,actualPermissionOrServiceChanges=0,coverage=None,
         actualHarukaNormalStaticAndSixtyAndPost='NOT_RUN',formalAcceptanceAdded=0)
(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,localToolAssertions=len(results),remoteConnections=0,productTestsExecuted=0)))
