"""Recover already completed analyzer output only; never rerun58 or its analyzer."""
from pathlib import Path
import datetime
import hashlib
import json
import xml.etree.ElementTree as ET

root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001';output=base/'evidence/PG33738-readwire58-unfiltered-same-exec-v1'
load=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();ref=lambda path:dict(path=str(path.relative_to(root)),sha256=sha(path))
assert not (output/'manifest.json').exists()
postpath=base/'evidence/PG33736-readwire58-independent-v1/manifest.json';post=load(postpath);stage=load(output/'analysis-exit.json');assert post['actualExit']==stage['actualExit']==0 and post['tests']==58
assert all(sha(root/path)==value for path,value in post['inputHashes'].items())
classes={};methods=[]
for line in (output/'analysis.stdout').read_text().splitlines():
    fields=line.split('\t')
    if fields[0]=='CLASS':
        assert len(fields)==12;name=fields[1];assert name not in classes
        row=dict(name=name,id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[name]=row;start=6
    else:
        assert fields[0]=='METHOD' and len(fields)==11;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);start=5
    for item in fields[start:]:
        kind,missed,covered=item.split(':');row['counters'][kind]=dict(missed=int(missed),covered=int(covered))
assert len(classes)==194 and set(classes)==set(post['classIds']) and all(row['id']==post['classIds'][name] for name,row in classes.items())
for name,row in classes.items():assert sum(row['counters']['METHOD'].values())==post['actualJvmCodeMethodCounts'][name]
assert len(methods)==1522
default={node.get('name'):node for node in ET.parse(postpath.parent/'original-coverage.xml').getroot().findall('.//class')}
def defaults(name):
    node=default.get(name)
    if node is None:return set()
    return {(method.get('name'),method.get('desc')) for method in node.findall('method') if any(counter.get('type')=='METHOD' and int(counter.get('missed'))+int(counter.get('covered'))>0 for counter in method.findall('counter'))}
filtered=[method for method in methods if (method['name'],method['descriptor']) not in defaults(method['className'])];assert len(filtered)==719
def aggregate(names):
    return {kind:dict(missed=sum(classes[name]['counters'][kind]['missed'] for name in names),covered=sum(classes[name]['counters'][kind]['covered'] for name in names)) for kind in next(iter(classes.values()))['counters']}
all_counter=aggregate(classes);web=aggregate([name for name in classes if '/web/' in name]);missing=[method for method in methods if '/web/' in method['className'] and any(value['missed'] for value in method['counters'].values())]
assert web['METHOD']==dict(missed=0,covered=73) and web['BRANCH']==dict(missed=0,covered=82) and web['INSTRUCTION']==dict(missed=9,covered=1317) and web['LINE']==dict(missed=1,covered=287)
assert len(missing)==1 and missing[0]['name']=='sameContext' and missing[0]['className']=='dev/codex/schubert/nk/web/messaging/ProtectedReadWireClient'
report=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),kind='MEASUREMENT_RECOVERY_OWN_RAW_UNACCEPTED',source=post['productionCoreMain'],productionCoreMain=post['productionCoreMain'],actualUnitSource=post['source'],originalPost=ref(postpath),originalSingleExec=ref(postpath.parent/'jacoco.exec'),analysisExit=ref(output/'analysis-exit.json'),analysisStdout=ref(output/'analysis.stdout'),classes=classes,methods=methods,defaultFilteredMethods=filtered,rawCounterClassSum=all_counter,defaultCounter=post['coverage'],webDiagnosticOnly=web,own13Source18Physical16CodeRawFour100=False,ownInstructionAndLineGap=missing,all194ScopeAccepted=False,physicalClasses=194,actualCodeMethods=1522,defaultMethods=803,filteredMethodDifference=719,recoveredFromExistingOutput=True,analyzerReexecuted=False,applicationTestsExecuted=0,originalGuardToolExit=1,originalGuard='3458 expected ownRaw allmiss0 rejected9I/1L before report; no acceptance',oldExecCombined=False,sourceHashesCurrent189Verified=True,productionBinaryClassDefinitionOrInitialization=0,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None)
(output/'manifest.json').open('x').write(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,recoveryOnly=True,ownRaw=web,ownRawAccepted=False,sameContextMissingInstruction9Line1=True,unit58Replayed=False,analyzerReplayed=False)))
