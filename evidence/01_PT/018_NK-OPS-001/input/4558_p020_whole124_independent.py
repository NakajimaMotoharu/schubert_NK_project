"""Independently bind original single remote terminal, all124 XML, CRC and unfiltered counters."""
from pathlib import Path
import collections
import datetime
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
p=w/'pg37012-p020-remote124-recovered';unit=load(p/'terminal.json');begin=load(p/'begin.json');audit=load(b/'evidence/PG37004-p020-whole-scope-audit-v1/manifest.json');cfg=load(w/'pg37008-p020-public-package-v1/package.json')
assert sha(p/'terminal.json')=='8969246805b8acc095c9be26845ebebf2d0f237fca5bf41d2dded13e46d50681'
assert unit['actualExit']==0 and unit['source']==audit['actualUnitSource']==cfg['source'] and unit['sourceCore']==audit['sourceCore']
assert all(v['actualExit']==0 and not v['timedOut'] for v in unit['stages'].values())
assert unit['sourceInputsUnchanged'] and unit['baselineUnchanged'] and begin['sourceHashes']==cfg['sourceHashes']
assert all(sha(r/path)==h for path,h in cfg['sourceHashes'].items())
assert all(sha(p/name)==h for name,h in unit['files'].items())
assert all(sha(p/'mainclasses'/name)==h for name,h in unit['mainClasses'].items())
assert all(sha(p/'testclasses'/name)==h for name,h in unit['testClasses'].items())
assert not any('CurrentCharacterizationTest' in name or 'Native' in name for name in unit['testClasses'])
def valid_case(c):return not any(c.findall('.//'+tag) for tag in ['failure','error','skipped']) and all(x.tag in ['system-out','system-err'] for x in c)
assert valid_case(ET.fromstring('<testcase><system-out>metadata</system-out></testcase>'))
for tag in ['failure','error','skipped','unknown']:assert not valid_case(ET.fromstring('<testcase><'+tag+'/></testcase>'))
expected=set()
for suite in audit['selectedWholeSuites']:
 for method in suite['ordinaryMethods']:expected.add(('dev.codex.schubert.characterization.'+suite['suite'],method+'()'))
 if suite['parameterizedInvocations']:
  for i in range(1,8):expected.add(('dev.codex.schubert.characterization.'+suite['suite'],'rejectsEveryNonPassExecutionStatus(String)['+str(i)+']'))
cases=[]
for name,h in unit['xmlHashes'].items():
 assert sha(p/'xml'/name)==h;tree=ET.parse(p/'xml'/name).getroot()
 assert all(int(tree.get(k,0))==0 for k in ['failures','errors','skipped'])
 for c in tree.findall('testcase'):assert valid_case(c);cases.append((c.get('classname'),c.get('name')))
assert len(cases)==len(set(cases))==len(expected)==124 and set(cases)==expected
ex=(p/'execinfo.log').read_text();assert ex.count('Session "')==1 and 'Session "PG37012-COMMON124"' in ex
initializing=set(re.findall(r"Initializing '([^']+)'",(p/'class-init.log').read_text()))
assert not any(n.startswith(('dev/codex/schubert/nk/','com/microsoft/playwright/')) for n in initializing)
assert 'dev/codex/schubert/characterization/CurrentCharacterizationTest' not in initializing
probes={n:dict(crc=crc,hit=int(hit),total=int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
def crc64(raw):
 assert int.from_bytes(raw[6:8],'big')==69
 value=0
 for byte in raw:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
ids={name[:-6]:crc64((p/'mainclasses'/name).read_bytes()) for name in unit['mainClasses']}
assert set(n for n in probes if n.startswith('dev/codex/schubert/characterization/') and n in ids)==set(ids)
assert all(probes[n]['crc']==h and probes[n]['hit']>0 for n,h in ids.items())
qualified=load(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');selftest=load(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json');assert selftest['actualExit']==0 and selftest['toolTests']==12
for pin in qualified['dependencies']+[dict(path=str(r/qualified['source']['path']),sha256=qualified['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
out=b/'evidence/PG37014-p020-whole124-independent-v1';assert not out.exists();out.mkdir()
cmd=[str(tc/'jdk-25.0.4/bin/java'),'-cp',':'.join([str(w/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),*[x['path'] for x in qualified['dependencies']]]),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(p/'jacoco.exec'),*[str(p/'mainclasses'/n) for n in sorted(unit['mainClasses'])]]
with (out/'unfiltered.stdout').open('xb') as stdout,(out/'unfiltered.stderr').open('xb') as stderr:
 child=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=120)
assert child.returncode==0
classes={};methods=[]
for line in (out/'unfiltered.stdout').read_text().splitlines():
 fields=line.split('\t')
 if fields[0]=='CLASS':
  assert len(fields)==12;row=dict(name=fields[1],id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[fields[1]]=row;offset=6
 else:
  assert fields[0]=='METHOD' and len(fields)==11;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);offset=5
 for item in fields[offset:]:
  key,miss,hit=item.split(':');row['counters'][key]=dict(missed=int(miss),covered=int(hit))
assert set(classes)==set(ids) and all(row['id']==ids[name] for name,row in classes.items())
totals={k:{role:sum(c['counters'][k][role] for c in classes.values()) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
standard={x.get('type'):dict(missed=int(x.get('missed')),covered=int(x.get('covered'))) for x in ET.parse(p/'coverage.xml').getroot().findall('counter')}
assert all(standard[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for name in ['terminal.json','begin.json','jacoco.exec','coverage.xml','execinfo.log','maincompile.log','testcompile.log','unit.log']:
 shutil.copyfile(p/name,out/name)
shutil.copytree(p/'xml',out/'xml')
with (out/'class-init.log.gz').open('xb') as f:f.write(gzip.compress((p/'class-init.log').read_bytes(),mtime=0))
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=unit['source'],sourceCore=unit['sourceCore'],run='PG37012-COMMON124',expected=124,success=124,failed=0,errors=0,skipped=0,notRun=0,wholeSuites=17,mainSources=5,mainPhysical=10,testHelperPhysical=31,cases=[dict(className=c,name=n,result='PASS') for c,n in sorted(cases)],standardCounters=standard,rawCounters=totals,rawMissedMethods=[m for m in methods if any(x['missed'] for x in m['counters'].values())],classIds=ids,classSha256=unit['mainClasses'],testHelperSha256=unit['testClasses'],classMeasurements=classes,sourceTestPins=cfg['sourceHashes'],sdkPins=cfg['sdkHashes'],sourceBaselineUnchanged=True,xmlNegativeChecks=4,realProductNativeBrowserDbRootInitializations=0,oldExecUnion=False,manualCoverageExclusions=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,scopeAudit=ref(b/'evidence/PG37004-p020-whole-scope-audit-v1/manifest.json'),files={str(x.relative_to(out)):sha(x) for x in sorted(out.rglob('*')) if x.is_file()},unfilteredCommand=cmd,unfilteredExit=child.returncode)
(out/'manifest.json').open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,success=124,standard=standard,raw=totals,rawMissingMethods=[(m['className'],m['name'],m['descriptor']) for m in value['rawMissedMethods']],newAcceptance=0)))
