"""Read-only measurement of two historical exact-source single-exec pure exception runs."""
from pathlib import Path
import datetime,hashlib,json,subprocess,xml.etree.ElementTree as ET
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));wr=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
compiled=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');selftest=ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json');assert selftest['actualExit']==0 and selftest['toolTests']==12
for pin in compiled['dependencies']+[dict(path=str(r/compiled['source']['path']),sha256=compiled['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
cp=':'.join([str(w/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),*[p['path'] for p in compiled['dependencies']]])
def crc(binary):
 assert int.from_bytes(binary[6:8],'big')==69
 v=0
 for byte in binary:
  v^=byte
  for _ in range(8):v=(v>>1)^0xd800000000000000 if v&1 else v>>1
 return f'{v:016x}'
out=b/'evidence/PG35240-exception-helper-existing-raw-audit-v1';assert not out.exists();out.mkdir();reports=[]
for label,postname,expected in [('morning','PG29898-morning-pure-sql12-post-v4',12),('jdbc','PG28380-jdbc-knownpair8-post-v1',8)]:
 pp=b/'evidence'/postname/'manifest.json';p=ld(pp);cfgpath=r/p['config']['path'];assert sha(cfgpath)==p['config']['sha256'];cfg=ld(cfgpath);prep=r/cfg['slots']['prepare']/'manifest.json';pr=ld(prep);assert pr['actualExit']==p['actualExit']==0 and p['tests']==expected
 names=sorted(pr['physicalClassHashes']);assert len(names)==4 and set(names)==set(cfg['physicalClasses'])
 for n in names:policy.relative_name(n)
 files=[w/cfg['privateDirs']['prepare']/'component'/n for n in names];before={n:sha(f) for n,f in zip(names,files)};assert before==pr['physicalClassHashes'];ids={n[:-6]:crc(f.read_bytes()) for n,f in zip(names,files)};assert ids==p['classIds']
 sourcehash={n:sha(r/n) for n in p['inputHashes'] if n.endswith('.java')};assert all(h==p['inputHashes'][n] for n,h in sourcehash.items());assert len(sourcehash)==4
 ex=pp.parent/'jacoco.exec';xx=pp.parent/'original-coverage.xml';assert sha(ex)==p['files']['jacoco.exec'] and sha(xx)==p['files']['original-coverage.xml'];xml={x.attrib['name']:x for x in ET.parse(xx).getroot().findall('.//package/class')}
 command=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(ex),*map(str,files)];s=subprocess.run(command,capture_output=True,timeout=60);(out/(label+'.stdout')).open('xb').write(s.stdout);(out/(label+'.stderr')).open('xb').write(s.stderr);assert s.returncode==0,s.stderr.decode()[:600]
 classes={};methods=[]
 for line in s.stdout.decode().splitlines():
  fields=line.split('\t')
  if fields[0]=='CLASS':
   assert len(fields)==12;name=fields[1];assert name not in classes;row=dict(name=name,id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[name]=row;start=6
  else:
   assert fields[0]=='METHOD' and len(fields)==11;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);start=5
  for item in fields[start:]:
   k,mi,co=item.split(':');row['counters'][k]=dict(missed=int(mi),covered=int(co))
 assert set(classes)==set(ids) and all(c['id']==ids[n] for n,c in classes.items())
 for n,c in classes.items():assert sum(c['counters']['METHOD'].values())==p['actualJvmCodeMethodCounts'][n]
 default={(n,m.attrib['name'],m.attrib['desc']) for n,x in xml.items() for m in x.findall('method') if any(c.attrib['type']=='METHOD' and int(c.attrib['missed'])+int(c.attrib['covered'])>0 for c in m.findall('counter'))}
 filtered=[m for m in methods if (m['className'],m['name'],m['descriptor']) not in default];missed=[m for m in methods if m['counters']['METHOD']['missed']];counters={k:dict(missed=sum(c['counters'][k]['missed'] for c in classes.values()),covered=sum(c['counters'][k]['covered'] for c in classes.values())) for k in next(iter(classes.values()))['counters']}
 assert sum(counters['METHOD'].values())==len(methods) and len(filtered)==len(methods)-sum(p['coverage']['METHOD'].values());assert before=={n:sha(f) for n,f in zip(names,files)} and sha(ex)==p['files']['jacoco.exec'];assert all(sha(r/n)==h for n,h in sourcehash.items())
 report=dict(label=label,actualExit=0,historicalUnitSource=p['source'],historicalCore=p['productionCoreMain'],historicalTestsReferenced=expected,currentRelevantMainAndTestSourceExact=True,originalPost=ref(pp),config=ref(cfgpath),prepare=ref(prep),singleOriginalExec=ref(ex),originalCoverageXml=ref(xx),physicalClassHashes=before,classIds=ids,rawCounters=counters,defaultCounters=p['coverage'],defaultFilteredMethods=filtered,missedCodeMethods=missed,classes=classes,methods=methods,actualCodeMethods=len(methods),toolSelftest12ReferenceOnly=True,applicationTestsExecuted=0,productClassDefinitionOrInitialization=0,oldSourcesOrExecsCombined=False,sourceHashes=sourcehash,command=command);wr(out/(label+'.json'),report);reports.append(dict(label=label,report=ref(out/(label+'.json')),rawCounters=counters,missedMethods=[dict(className=m['className'],name=m['name'],descriptor=m['descriptor']) for m in missed]))
manifest=dict(actualExit=0,source='deaed367cb4f234af95fe9e96014f6c01e30486d',productionCoreMain='deaed367cb4f234af95fe9e96014f6c01e30486d',terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),runs=reports,applicationTestsExecuted=0,historicalTestsReferenced=20,physicalReadsAdmittedNamesOnly=True,sourceSpecificRunsKeptSeparate=True,oldSuccessPromotedToCurrentCore=False,formalUpdated=False,newAcceptance=0,effortRate=None);wr(out/'manifest.json',manifest);print(json.dumps(dict(actualExit=0,reports=reports,applicationTestsExecuted=0),ensure_ascii=False))
