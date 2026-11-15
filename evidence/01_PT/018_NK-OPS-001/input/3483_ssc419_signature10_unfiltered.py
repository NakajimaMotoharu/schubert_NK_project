"""Supplement the same public-RFC verification exec, without initializing production or replay."""
from pathlib import Path
import datetime,hashlib,json,subprocess,xml.etree.ElementTree as ET
import pgpt_closed_host_profile as h
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=ld(b/'input/3480_ssc419_signature10_profile.json');pp=r/c['slots']['post']/'manifest.json';p=ld(pp);prepared=ld(r/c['slots']['prepare']/'manifest.json');assert p['actualExit']==0 and p['tests']==10 and p['source']=='5c470b48941b45691b1680568f9c275d7b14f931'
assert all(sha(r/n)==v for n,v in p['inputHashes'].items())
names=sorted(prepared['physicalClassHashes']);assert len(names)==5
for n in names:h.relative_name(n)
folder=r.parent/'pgpt-runs/PG379'/c['privateDirs']['prepare']/'component';files=[folder/n for n in names];assert {n:sha(q) for n,q in zip(names,files)}==prepared['physicalClassHashes']
exe=pp.parent/'jacoco.exec';xml=pp.parent/'original-coverage.xml';assert sha(exe)==p['files']['jacoco.exec'] and sha(xml)==p['files']['original-coverage.xml']
tool=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');test=ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json');assert test['actualExit']==0 and test['toolTests']==12
for pin in tool['dependencies']+[dict(path=str(r/tool['source']['path']),sha256=tool['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
e=b/'evidence/PG33774-ssc419-signature10-unfiltered-v1';assert not e.exists();e.mkdir();work=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1';cp=':'.join([str(work/'toolclasses'),*[v['path'] for v in tool['dependencies']]])
cmd=[str(h.JAVA),'-cp',cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(exe),*map(str,files)];start=datetime.datetime.now(datetime.timezone.utc).isoformat();result=subprocess.run(cmd,capture_output=True,timeout=60)
(e/'analysis.stdout').open('xb').write(result.stdout);(e/'analysis.stderr').open('xb').write(result.stderr);assert result.returncode==0
classes={};methods=[]
for line in result.stdout.decode().splitlines():
 fields=line.split('\t')
 if fields[0]=='CLASS':
  assert len(fields)==12;row=dict(name=fields[1],id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[fields[1]]=row;begin=6
 else:
  assert fields[0]=='METHOD' and len(fields)==11;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);begin=5
 for item in fields[begin:]:
  kind,miss,cover=item.split(':');row['counters'][kind]=dict(missed=int(miss),covered=int(cover))
assert set(classes)==set(p['classIds']) and all(v['id']==p['classIds'][n] for n,v in classes.items())
assert len(methods)==sum(p['actualJvmCodeMethodCounts'].values())
for n,row in classes.items():assert sum(row['counters']['METHOD'].values())==p['actualJvmCodeMethodCounts'][n]
def counters(names):return {kind:dict(missed=sum(classes[n]['counters'][kind]['missed'] for n in names),covered=sum(classes[n]['counters'][kind]['covered'] for n in names)) for kind in next(iter(classes.values()))['counters']}
all_counter=counters(classes);own=counters(c['targetClasses']);qualified=all(v['missed']==0 and v['covered']>0 for v in own.values());default={node.get('name'):node for node in ET.parse(xml).getroot().findall('.//class')}
filtered=[]
for method in methods:
 node=default.get(method['className']);original={(v.get('name'),v.get('desc')) for v in node.findall('method')} if node is not None else set()
 if (method['name'],method['descriptor']) not in original:filtered.append(method)
assert all(sha(r/n)==v for n,v in p['inputHashes'].items()) and sha(exe)==p['files']['jacoco.exec']
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=p['productionCoreMain'],productionCoreMain=p['productionCoreMain'],actualUnitSource=p['source'],actualAnalyzerExit=result.returncode,command=cmd,startUTC=start,independentPost=ref(pp),originalSingleExec=ref(exe),analysisStdout=ref(e/'analysis.stdout'),classes=classes,methods=methods,physicalClasses=5,actualCodeMethods=len(methods),ownCounters=own,wholeCounters=all_counter,ownAllCounters100=qualified,wholeScopeAccepted=False,filteredMethods=filtered,manualExclusions=[],oldExecCombined=False,toolSelftest12Replayed=False,applicationTestsExecuted=0,productionClassDefinedOrInitialized=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawOwn=own,ownQualified=qualified,whole5=all_counter,actualCodeMethods=len(methods),filtered=len(filtered))))
