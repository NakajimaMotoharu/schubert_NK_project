"""Eight independent boundary checks; execute only the pure validator AST, no event producer."""
from pathlib import Path
import ast,copy,hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=B/'input/1100_wbs65_stage_record_v2.py';tree=ast.parse(p.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate_forecast_additional_boundary'];assert len(nodes)==1;scope={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),scope);check=scope['validate_forecast_additional_boundary'];rows=[]
def case(name,body):
 body();rows.append(dict(id=name,actualExit=0))
def reject(value,reason):
 try:check(value)
 except ValueError as e:assert str(e).startswith(reason)
 else:raise AssertionError('invalid estimate accepted')
def fixture(gross=(7.9,22.4,44.8),completed=(7.9,22.4,44.8),remaining=(0,0,0)):
 return {n:dict(zip(['low','base','high'],v)) for n,v in zip(['additionalRequiredWorkGrossPp','additionalCompletedWorkPp','additionalDiscoveredRemainingPp'],[gross,completed,remaining])}
case('TOOL-ESTIMATE-001-ZERO',lambda:check(fixture((0,0,0),(0,0,0))))
case('TOOL-ESTIMATE-002-CURRENT-EXACT',lambda:check(fixture()))
case('TOOL-ESTIMATE-003-DECIMAL-PENDING',lambda:check(fixture((8,22.7,45.4),remaining=(.1,.3,.6))))
case('TOOL-ESTIMATE-004-MISSING-NULL',lambda:reject({},'FORECAST_ADDITIONAL_FIELDS'))
case('TOOL-ESTIMATE-005-LEGACY-OMISSION',lambda:reject(fixture((4.975,13.775,27.55)),'FORECAST_ADDITIONAL_GROSS_MISMATCH'))
def bad_values():
 for invalid in [True,-1,float('nan'),float('inf'),'22.4',None]:
  v=fixture();v['additionalRequiredWorkGrossPp']['base']=invalid;reject(v,'FORECAST_ADDITIONAL_VALUE')
case('TOOL-ESTIMATE-006-BAD-VALUE',bad_values)
def bad_shape():
 for value in [None,[],dict(low=1,base=2,high=3,unknown=0),dict(low=1,base=2)]:
  v=fixture();v['additionalRequiredWorkGrossPp']=value;reject(v,'FORECAST_ADDITIONAL_FIELDS')
case('TOOL-ESTIMATE-007-BAD-SHAPE',bad_shape)
case('TOOL-ESTIMATE-008-ORDER',lambda:reject(fixture((30,22.4,44.8)),'FORECAST_ADDITIONAL_ORDER'))
assert len(rows)==8;O=B/'evidence/PG27760-estimate-boundary-tool-eight-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,cases=rows,toolChecks=8,productTestsExecuted=0,validatorPath=str(p.relative_to(R)),validatorSha256=hashlib.sha256(p.read_bytes()).hexdigest(),onlyPureAstExecuted=True,eventsWritten=0,actualCost=None,producerSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolChecks=8,manifestSha256=hashlib.sha256((O/'manifest.json').read_bytes()).hexdigest())))
