"""BUG2708/YKT2375 independent full-line/multiplicity and foreign-source safety vectors."""
from pathlib import Path
import ast,hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=B/'input/1634_web_security_fatal_source_static.py';tree=ast.parse(p.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['revert_calls','require_owned']];assert len(nodes)==2;ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns);revert=ns['revert_calls'];owned=ns['require_owned'];old='header\nbody\n';planned='header\n  guard();\n    guard();\n  guard();\nbody\n';calls=['  guard();\n','    guard();\n','  guard();\n'];results=[]
assert revert(planned,calls)==old;results.append('TOOL-INVERSE001_DUPLICATE_AND_MIXED_INDENT_EXPECTED_EXACT_ORIGINAL')
for id,candidate in [('TOOL-INVERSE002_MISSING_CALL',planned.replace('  guard();\n','',1)),('TOOL-INVERSE003_EXTRA_CALL',planned+'  guard();\n')]:
 try:revert(candidate,calls)
 except AssertionError as e:assert str(e)=='CALL_LINE_MULTIPLICITY_MISMATCH';results.append(id)
 else:raise AssertionError('invalid inserted multiplicity accepted')
assert owned(old,old,planned) is False and owned(planned,old,planned) is True;results.append('TOOL-INVERSE004_OWN_OLD_AND_SAVED_PLANNED_ALLOWED')
try:owned(planned+'foreign\n',old,planned)
except AssertionError as e:assert str(e)=='FOREIGN_SOURCE_CHANGE_REFUSED';results.append('TOOL-INVERSE005_FOREIGN_USER_CHANGE_REFUSED')
else:raise AssertionError('foreign source accepted')
assert len(results)==5;O=B/'evidence/PG27437-source-inverse-independent-negative-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,toolAssertions=5,results=results,producerSourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),productTestsExecuted=0,MainOrTestChanged=False,actualHeldClassOrBackendActions=0,bug='BUG-2708',horizontal='YKT-2375',scope='TOOL_LOGIC_ONLY_NOT_PRODUCT_PT_OR_COVERAGE',independentExpectedOriginalLiteral=True);(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolAssertions=5,productTestsExecuted=0)))
