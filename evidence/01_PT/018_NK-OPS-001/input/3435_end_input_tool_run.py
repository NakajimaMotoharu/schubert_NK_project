"""Execute only the12 pure tool tests with fixed source and new coverage output."""
from pathlib import Path
import datetime,hashlib,json,os,platform,subprocess,sys
r=Path.cwd();e=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG33720-end-checkpoint-input-tool-v1';tc=r.parent/'toolchain';source=['tools/quality/pmo_stage_input.py','tools/quality/tests/test_pmo_stage_input.py','evidence/01_PT/018_NK-OPS-001/input/1100_wbs65_stage_record_v2.py'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={n:sha(r/n) for n in source};head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
for n in source:assert subprocess.check_output(['git','show',head+':'+n])==(r/n).read_bytes()
assert not (e/'tool-test-result.json').exists();store=r.parent/'pgpt-runs/PG379/pg33720-end-input-coverage';assert not store.exists();store.mkdir(mode=0o700)
env=dict(os.environ,PYTHONPATH=os.pathsep.join(map(str,[tc/'coverage-7.17.3/runtime',tc/'pyflakes-3.4.0/runtime',r/'tools/quality'])),COVERAGE_FILE=str(store/'coverage.sqlite'))
commands=[('unittest',[sys.executable,'-B','-m','coverage','run','--branch','--source=pmo_stage_input','-m','unittest','discover','-s','tools/quality/tests','-p','test_pmo_stage_input.py','-v']),('coverage-json',[sys.executable,'-B','-m','coverage','json','-o',str(e/'coverage.json')]),('coverage-report',[sys.executable,'-B','-m','coverage','report','--fail-under=100']),('pyflakes',[sys.executable,'-B','-m','pyflakes',*source])]
stages={}
for name,command in commands:
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();x=subprocess.run(command,env=env,capture_output=True,timeout=60);(e/(name+'.stdout')).open('xb').write(x.stdout);(e/(name+'.stderr')).open('xb').write(x.stderr);stages[name]=dict(command=command,actualExit=x.returncode,startedUTC=started,completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(e/(name+'-exit.json')).open('x').write(json.dumps(stages[name],indent=2)+'\n');print(name,x.returncode)
 if x.returncode:print(x.stderr.decode()[-2000:]);raise SystemExit(x.returncode)
c=json.loads((e/'coverage.json').read_text());assert list(c['files'])==['tools/quality/pmo_stage_input.py'];t=c['totals'];assert t['missing_lines']==t['missing_branches']==t['excluded_lines']==0 and t['percent_covered']==100
assert pins=={n:sha(r/n) for n in source};text=(e/'unittest.stderr').read_text();assert 'Ran 12 tests' in text and text.rstrip().endswith('OK') and 'skipped=' not in text
result=dict(actualExit=0,operatorSource=head,sourceHashes=pins,stages=stages,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,os=platform.platform(),toolTests=12,failed=0,errors=0,skipped=0,coverage=t,coverageScope='NEW_PURE_PMO_STAGE_INPUT_MODULE_ONLY_NOT_WHOLE_RECORDER_OR_APPLICATION',productTestsExecuted=0,actualSDKorJavaVmDbNativeRootOperations=0,original5402Reissued=False,formalUpdated=False,effortRate=None)
(e/'tool-test-result.json').open('x').write(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,toolTests=12,coverage=t,productTests=0))
