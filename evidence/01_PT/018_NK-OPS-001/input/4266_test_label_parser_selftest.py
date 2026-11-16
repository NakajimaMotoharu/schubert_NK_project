"""BUG3109/YKT2581: exact expected-case recognition, no application tests or held source reads."""
from pathlib import Path
import hashlib,json,tempfile
import pgpt_closed_host_profile as p
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();checks=[]
with tempfile.TemporaryDirectory(prefix='pg36069-label-parser-',dir=r.parent/'pgpt-runs/PG379') as w:
 f=Path(w)/'Example.java'
 def check(text,expected):
  f.write_text('package example; class Example {\n'+text+'\n}');c=dict(testSources=[dict(path=str(f),tests=len(expected))],expectedTests=len(expected));actual=p.expected_cases(c);assert [v['name'] for v in actual]==expected;checks.append(dict(expected=expected,passed=True))
 check('@Test\nvoid ordinary() {}',['ordinary()'])
 check('@Test // TestID 001\nvoid labeled() {}',['labeled()'])
 check('@Test // void fake() TestID\nvoid actual() {}',['actual()'])
 check('@Test\n@Timeout(1)\nvoid timed() {}',['timed()'])
 check('@Test // TestID\r\nvoid windows() {}',['windows()'])
 check('@Test void sameLine() {}',['sameLine()'])
 f.write_text('package example; class Example { @Test void one() {} }');c=dict(testSources=[dict(path=str(f),tests=2)],expectedTests=2)
 try:p.expected_cases(c)
 except ValueError as e:assert str(e)=='whole Test method count changed';checks.append(dict(countMismatchRejected=True,passed=True))
 else:raise AssertionError('count guard not preserved')
for name,count in [('4263_ssc443_path_profile.json',5),('4246_wire_enum_value4_profile.json',4)]:
 c=json.loads((b/'input'/name).read_text());cases=p.expected_cases(c);assert len(cases)==count and len({(v['classname'],v['name']) for v in cases})==count;checks.append(dict(profile=name,exactCases=count,passed=True))
o=b/'evidence/PG36069-test-label-parser-selftest-v1';o.mkdir();v=dict(actualExit=0,toolChecks=len(checks),checks=checks,toolSha256=sha(r/'tools/quality/pgpt_closed_host_profile.py'),originalFixtureChanged=False,applicationTestsExecuted=0,heldOperations=0);(o/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolChecks=len(checks),applicationTestsExecuted=0)))
