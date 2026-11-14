"""Independently supplement the fresh same-source176 post with unfiltered exact Code counters."""
from pathlib import Path
import hashlib,json,datetime,subprocess,sys,re,xml.etree.ElementTree as ET
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pfpath=b/'input/2850_speaker_read176_fixture_fixed_profile.json';pf=load(pfpath);policy.validate_syntax(pf);names=pf['physicalClasses'];assert len(names)==len(set(names))==18
# The existing guard rejects all held names before any .class stat/read/hash.
for name in names:policy.relative_name(name)
postdir=r/pf['slots']['post'];post=load(postdir/'manifest.json');assert len(sys.argv)==2 and re.fullmatch('[0-9a-f]{40}',sys.argv[1]);assert post['source']==sys.argv[1] and post['productionCoreMain']==pf['productionCoreMain'] and post['tests']==176 and post['positiveMainCrc']==18 and post['wholeScopeFour100'];assert set(n[:-6] for n in names)==set(post['classIds'])==set(post['actualJvmCodeMethodCounts']);execpath=postdir/'jacoco.exec';assert sha(execpath)==post['files']['jacoco.exec']
classdir=r.parent/'pgpt-runs/PG379'/pf['privateDirs']['prepare'];files=[classdir/'component'/name for name in names];before={str(p):sha(p) for p in files};prepared=load(r/pf['slots']['prepare']/'manifest.json');assert {name:before[str(path)] for name,path in zip(names,files)}==prepared['physicalClassHashes'];xmlpath=postdir/'original-coverage.xml';assert sha(xmlpath)==post['files']['original-coverage.xml'];defaultroot=ET.parse(xmlpath).getroot();defaultclasses={c.attrib['name']:c for c in defaultroot.findall('.//package/class')};assert set(defaultclasses)==set(post['classIds'])
compiled=load(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');selftest=load(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json');assert selftest['actualExit']==0 and selftest['toolTests']==12
# Also prove the full toy's instruction/line/class counters have no miss, without rerunning it.
full=selftest['tests'][0]['detail']['actual'];assert all(v['missed']==0 for c in full['classes'].values() for v in c['counters'].values())
for pin in compiled['dependencies']+[dict(path=str(r/compiled['source']['path']),sha256=compiled['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
def crc64(blob):
 assert int.from_bytes(blob[6:8],'big')==69
 value=0
 for byte in blob:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
independent_crc={name[:-6]:crc64(p.read_bytes()) for name,p in zip(names,files)};assert independent_crc==post['classIds']
e=b/'evidence/PG31988-speaker-read176-unfiltered-measurement-v1';e.mkdir();w=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1';cp=':'.join([str(w/'toolclasses'),*[p['path'] for p in compiled['dependencies']]]);cmd=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(execpath),*map(str,files)];now=datetime.datetime.now(datetime.timezone.utc).isoformat();result=subprocess.run(cmd,capture_output=True,timeout=60);(e/'analysis.stdout').write_bytes(result.stdout);(e/'analysis.stderr').write_bytes(result.stderr);(e/'analysis-exit.json').open('x').write(json.dumps(dict(command=cmd,actualExit=result.returncode,startUTC=now,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n');assert result.returncode==0,result.stderr.decode()[:1200]
classes={};methods=[]
for line in result.stdout.decode().splitlines():
 fields=line.split('\t')
 if fields[0]=='CLASS':
  assert len(fields)==12;name=fields[1];assert name not in classes;row=dict(name=name,id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[name]=row;start=6
 else:
  assert fields[0]=='METHOD' and len(fields)==11;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);start=5
 for item in fields[start:]:
  kind,miss,covered=item.split(':');row['counters'][kind]=dict(missed=int(miss),covered=int(covered))
assert set(classes)==set(independent_crc) and all(c['dataPresent'] and c['id']==independent_crc[name] for name,c in classes.items())
for name,c in classes.items():assert sum(c['counters']['METHOD'].values())==post['actualJvmCodeMethodCounts'][name]
def defaults(name):return {(m.attrib['name'],m.attrib['desc']) for m in defaultclasses[name].findall('method') if any(c.attrib['type']=='METHOD' and int(c.attrib['missed'])+int(c.attrib['covered'])>0 for c in m.findall('counter'))}
filtered=[m for m in methods if (m['name'],m['descriptor']) not in defaults(m['className'])];assert len(filtered)==sum(post['actualJvmCodeMethodCounts'].values())-sum(post['coverage']['METHOD'].values())
missed=[m for m in methods if m['counters']['METHOD']['missed']];counter={kind:dict(missed=sum(c['counters'][kind]['missed'] for c in classes.values()),covered=sum(c['counters'][kind]['covered'] for c in classes.values())) for kind in classes[names[0][:-6]]['counters']};assert sum(counter['METHOD'].values())==sum(post['actualJvmCodeMethodCounts'].values())==len(methods)
assert before=={str(p):sha(p) for p in files} and sha(execpath)==post['files']['jacoco.exec']
rawFour100=all(counter[k]['missed']==0 and counter[k]['covered']>0 for k in ['INSTRUCTION','LINE','METHOD','CLASS','BRANCH'])
report=dict(rawFour100=rawFour100,actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),measurementOnly=True,actualUnitSource=post['source'],productionCoreMain=post['productionCoreMain'],profile=ref(pfpath),originalPost=ref(postdir/'manifest.json'),originalSingleExec=ref(execpath),tool=ref(r/'tools/quality/jacoco/UnfilteredCodeMeasurement.java'),selftest=ref(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json'),classFileHashes=before,independentClassCrc=independent_crc,classes=classes,methods=methods,rawCounterClassSum=counter,defaultCounter=post['coverage'],defaultFilteredMethods=filtered,missedCodeMethods=missed,physicalClasses=len(names),actualCodeMethods=len(methods),defaultMethods=sum(post['coverage']['METHOD'].values()),filteredMethodDifference=len(filtered),allInputsUnchanged=True,applicationTestsExecuted=0,oldExecCombined=False,defaultFiltersOrReportsChanged=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None)
(e/'manifest.json').open('x').write(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=counter,default=post['coverage'],filteredMethods=len(filtered),missedCodeMethods=[dict(className=m['className'],name=m['name'],descriptor=m['descriptor']) for m in missed],appTestsExecuted=0)))
