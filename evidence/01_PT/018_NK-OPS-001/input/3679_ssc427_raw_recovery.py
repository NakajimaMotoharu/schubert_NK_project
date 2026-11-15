"""Recover analyzer0 only; preserve two real role-switch branch misses without replay."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as ET
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
e=b/'evidence/PG34164-ssc427-verifier8-unfiltered-same-exec-v1';assert not (e/'manifest.json').exists();pp=b/'evidence/PG34162-ssc427-verifier8-independent-v1/manifest.json';p=ld(pp);stage=ld(e/'analysis-exit.json');assert stage['actualExit']==0 and p['actualExit']==0 and p['tests']==8
classes={};methods=[]
for line in (e/'analysis.stdout').read_text().splitlines():
 fields=line.split('\t')
 if fields[0]=='CLASS':
  assert len(fields)==12 and fields[1] not in classes;row=dict(name=fields[1],id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[fields[1]]=row;start=6
 else:
  assert fields[0]=='METHOD' and len(fields)==11;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);start=5
 for item in fields[start:]:
  kind,miss,hit=item.split(':');row['counters'][kind]=dict(missed=int(miss),covered=int(hit))
assert len(classes)==191 and set(classes)==set(p['classIds']) and all(v['id']==p['classIds'][n] and sum(v['counters']['METHOD'].values())==p['actualJvmCodeMethodCounts'][n] for n,v in classes.items())
def aggregate(names):return {kind:dict(missed=sum(classes[n]['counters'][kind]['missed'] for n in names),covered=sum(classes[n]['counters'][kind]['covered'] for n in names)) for kind in next(iter(classes.values()))['counters']}
targets=p['declaredTargets'];assert len(targets)==2;own=aggregate(targets);required=['LINE','METHOD','CLASS','BRANCH'];four=all(own[k]['missed']==0 and own[k]['covered']>0 for k in required)
assert four is False and own==dict(INSTRUCTION=dict(missed=0,covered=413),BRANCH=dict(missed=2,covered=30),LINE=dict(missed=0,covered=102),COMPLEXITY=dict(missed=2,covered=23),METHOD=dict(missed=0,covered=8),CLASS=dict(missed=0,covered=2))
extra=[v for v in methods if v['className'] in targets and any(q['missed'] for q in v['counters'].values())];assert len(extra)==1 and extra[0]['name']=='readRole' and extra[0]['counters']['BRANCH']['missed']==2
original=ET.parse(pp.parent/'original-coverage.xml').getroot();default={n.get('name'):n for n in original.findall('.//class')};filtered=[]
for v in methods:
 node=default.get(v['className']);names={(q.get('name'),q.get('desc')) for q in node.findall('method')} if node is not None else set()
 if (v['name'],v['descriptor']) not in names:filtered.append(v)
assert all(sha(r/n)==h for n,h in p['inputHashes'].items()) and sha(pp.parent/'jacoco.exec')==p['files']['jacoco.exec']
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=p['productionCoreMain'],productionCoreMain=p['productionCoreMain'],actualUnitSource=p['source'],actualAnalyzerExit=0,originalQualityGuardExit=1,recoveryOnly=True,analyzerReexecuted=False,applicationTestsExecuted=0,originalPost=ref(pp),originalSingleExec=ref(pp.parent/'jacoco.exec'),analysisExit=ref(e/'analysis-exit.json'),analysisStdout=ref(e/'analysis.stdout'),classes=classes,methods=methods,physicalClasses=191,actualCodeMethods=len(methods),defaultFilteredMethods=filtered,filteredMethodDifference=len(filtered),rawCounterClassSum=aggregate(classes),defaultCounter=p['coverage'],apiDiagnosticOnly=aggregate([n for n in classes if '/api/' in n]),declaredTargets=targets,targetIssueAuditCounters=own,requiredCounterNames=required,targetIssueAuditRawFour100=False,unexecutedTargetMethods=extra,unexecutedInstructions0=True,unexecutedRequiredBranches2=True,unexecutedRequiredLines0=True,originalQualityGuardCorrectlyRejected=True,manualExclusions=0,unreachableClassificationAdded=False,defaultFiltersChanged=False,oldExecCombined=False,all191ScopeAccepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,targetRequiredFour100=False,unexecutedRequiredBranches2=True,ownCounters=own,physical=191,unitAndAnalyzerReplayed=False)))
