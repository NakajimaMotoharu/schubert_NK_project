"""Recover the completed raw analyzer; enforce exactly the mandatory four from451, preserve all six."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as ET
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
e=b/'evidence/PG33794-ssc420-encrypt27-unfiltered-same-exec-v1';assert not (e/'manifest.json').exists();pp=b/'evidence/PG33792-ssc420-encrypt27-independent-v1/manifest.json';p=ld(pp);stage=ld(e/'analysis-exit.json');assert stage['actualExit']==0 and p['actualExit']==0 and p['tests']==27
policy=r/'documents/400_PGPT/450_品質/451_Build・静的解析・coverage方針.md';text=policy.read_text();assert '- Line 100%、method 100%、class 100%、branch 100%を小数丸め前のcounterで判定する。' in text
required=['LINE','METHOD','CLASS','BRANCH'];classes={};methods=[]
for line in (e/'analysis.stdout').read_text().splitlines():
 fields=line.split('\t')
 if fields[0]=='CLASS':
  assert len(fields)==12 and fields[1] not in classes;row=dict(name=fields[1],id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[fields[1]]=row;start=6
 else:
  assert fields[0]=='METHOD' and len(fields)==11;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);start=5
 for item in fields[start:]:
  kind,miss,hit=item.split(':');row['counters'][kind]=dict(missed=int(miss),covered=int(hit))
assert len(classes)==191 and set(classes)==set(p['classIds']) and all(row['id']==p['classIds'][name] for name,row in classes.items())
for name,row in classes.items():assert sum(row['counters']['METHOD'].values())==p['actualJvmCodeMethodCounts'][name]
assert len(methods)==sum(p['actualJvmCodeMethodCounts'].values())
def aggregate(names):return {kind:dict(missed=sum(classes[n]['counters'][kind]['missed'] for n in names),covered=sum(classes[n]['counters'][kind]['covered'] for n in names)) for kind in next(iter(classes.values()))['counters']}
allcounter=aggregate(classes);web=aggregate([n for n in classes if '/web/' in n]);targets=p['declaredTargetCodecs'];assert len(targets)==2;own=aggregate(targets)
four=all(own[k]['missed']==0 and own[k]['covered']>0 for k in required);all_six=all(v['missed']==0 and v['covered']>0 for v in own.values());assert four and all_six is False and own['INSTRUCTION']['missed']==12
extra=[v for v in methods if v['className'] in targets and any(q['missed'] for q in v['counters'].values())];assert len(extra)==2 and all(v['name']=='close' and v['counters']['INSTRUCTION']['missed']==6 and all(v['counters'][k]['missed']==0 for k in required) for v in extra)
default={n.get('name'):n for n in ET.parse(pp.parent/'original-coverage.xml').getroot().findall('.//class')};filtered=[]
for v in methods:
 node=default.get(v['className']);names={(q.get('name'),q.get('desc')) for q in node.findall('method')} if node is not None else set()
 if (v['name'],v['descriptor']) not in names:filtered.append(v)
assert all(sha(r/n)==h for n,h in p['inputHashes'].items()) and sha(pp.parent/'jacoco.exec')==p['files']['jacoco.exec']
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=p['productionCoreMain'],productionCoreMain=p['productionCoreMain'],actualUnitSource=p['source'],actualAnalyzerExit=0,originalGuardToolExit=1,recoveryOnly=True,analyzerReexecuted=False,applicationTestsExecuted=0,originalPost=ref(pp),originalSingleExec=ref(pp.parent/'jacoco.exec'),analysisExit=ref(e/'analysis-exit.json'),analysisStdout=ref(e/'analysis.stdout'),classes=classes,methods=methods,physicalClasses=191,actualCodeMethods=len(methods),defaultFilteredMethods=filtered,filteredMethodDifference=len(filtered),rawCounterClassSum=allcounter,defaultCounter=p['coverage'],webDiagnosticOnly=web,declaredTargetCodecs=targets,changed2CodecCounters=own,requiredCounterNames=required,changed2CodecRawFour100=four,changed2CodecRawAllSix100=all_six,unexecutedSupplementalInstructionMethods=extra,unexecutedSupplementalInstructions=12,noExceptionExecutionOrAllInstruction100Claim=True,mandatoryQualityRelaxed=False,coveragePolicy=ref(policy),manualExclusions=0,unreachableClassificationAdded=False,defaultFiltersChanged=False,oldExecCombined=False,all191ScopeAccepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,ownRequiredFour100=four,ownCounters=own,unexecutedInstruction12Retained=True,physical=191,wholeUnaccepted=True,unitAndAnalyzerReplayed=False)))
