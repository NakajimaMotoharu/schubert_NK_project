"""Tool-only ordinary eight cases, full scoped line/branch coverage and frozen producer identity."""
from pathlib import Path
import ast,datetime,hashlib,json,re,subprocess
import pg9666_pagination_static as capture
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';out=b/'evidence/PG33840-forecast-bridge-tool8-v1';work=r.parent/'pgpt-runs/PG379/pg33840-forecast-bridge-tool8-v1';assert not out.exists() and not work.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();paths=['tools/quality/pmo_forecast_bridge.py','tools/quality/tests/test_pmo_forecast_bridge.py',str(Path(__file__).resolve().relative_to(r))];inputs={p:sha(r/p) for p in paths}
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
node=next(n for n in ast.parse((r/paths[1]).read_text()).body if isinstance(n,ast.ClassDef));names=[n.name for n in node.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')];assert len(names)==8
work.mkdir();out.mkdir();capture.SLOT=out;capture.ENV=dict(capture.ENV,PYTHONPATH=':'.join(map(str,[r/'tools/quality',tc/'coverage-7.17.3/runtime',tc/'pyflakes-3.4.0/runtime'])))
data=work/'coverage.data';stages={};stages['pyflakes']=capture.step('pyflakes',['python3','-B','-m','pyflakes',*[str(r/p) for p in paths]],r)
stages['tool-unit']=capture.step('tool-unit',['python3','-B','-m','coverage','run','--branch','--source=pmo_forecast_bridge','--data-file='+str(data),'-m','unittest','discover','-s','tools/quality/tests','-p','test_pmo_forecast_bridge.py'],r)
for label,args in [('coverage-json',['json','--data-file='+str(data),'-o',str(out/'coverage.json')]),('coverage-report',['report','--data-file='+str(data),'--fail-under=100'])]:stages[label]=capture.step(label,['python3','-B','-m','coverage',*args],r)
assert all(v['actualExit']==0 and not v['timedOut'] for v in stages.values());stderr=(out/'tool-unit.stderr').read_text();assert re.search(r'Ran 8 tests in ',stderr) and '\nOK\n' in stderr and 'skipped=' not in stderr
coverage=json.loads((out/'coverage.json').read_text());assert len(coverage['files'])==1;name,item=next(iter(coverage['files'].items()));assert name.endswith('pmo_forecast_bridge.py') and item['missing_lines']==[] and item['missing_branches']==[] and item['excluded_lines']==[] and item['summary']['percent_covered']==100
assert all(sha(r/p)==h for p,h in inputs.items())
manifest=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),toolSource=source,inputHashes=inputs,testDefinitions=8,toolExecutions=8,success=8,failed=0,errors=0,skipped=0,caseNames=names,coverage=item['summary'],manualExclusions=[],coverageVersion=coverage['meta']['version'],stages=stages,environment=dict(python=subprocess.check_output(['python3','--version'],text=True).strip()),scope='ONLY_FORECAST_BRIDGE_HELPER_NOT_APPLICATION_OR_ALL_TOOLS',applicationTestsExecuted=0,originalBudgetChanged=False,actualCostOrEffortCompletionNotInferred=True,bug='BUG3024',horizontal='YKT2548')
(out/'manifest.json').open('x').write(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolTests=8,coverage=item['summary'],applicationTests=0)))
