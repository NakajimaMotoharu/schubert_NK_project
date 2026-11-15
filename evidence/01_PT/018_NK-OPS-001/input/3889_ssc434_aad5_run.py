"""Run original verifier6 plus resource-null2 once with current Main11."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import pg9666_pagination_static as capture
import pgpt_closed_host_profile as policy

root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001';tc=root.parent/'toolchain';runs=root.parent/'pgpt-runs/PG379'
load=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();ref=lambda path:dict(path=str(path.relative_to(root)),sha256=sha(path))
assert len(sys.argv)==2 and re.fullmatch('[0-9a-f]{40}',sys.argv[1]);unit_source=sys.argv[1]
producer_path=Path(__file__).resolve();producer_rel=str(producer_path.relative_to(root));assert sha(producer_path)==hashlib.sha256(subprocess.check_output(['git','show',unit_source+':'+producer_rel])).hexdigest()
prepared_path=base/'evidence/PG34706-ssc434-aad5-prepare-v1/manifest.json';prepared=load(prepared_path);admission_path=base/'evidence/PG34710-ssc434-aad5-preflight-v1/manifest.json';admission=load(admission_path)
assert admission['actualExit']==0 and admission['staticApplicable']==admission['unclassified']==0 and admission['expectedTests']==5
assert admission['inputHashes']==prepared['inputHashes'] and len(prepared['expectedCases'])==5
for path,value in prepared['inputHashes'].items():
    assert sha(root/path)==value
    assert hashlib.sha256(subprocess.check_output(['git','show',unit_source+':'+path])).hexdigest()==value
work=runs/'pg34706-ssc434-aad5-v1'
for name in list(prepared['physicalClassHashes'])+list(prepared['testClassHashes']):policy.relative_name(name)
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:assert {name:sha(work/folder/name) for name in prepared[key]}==prepared[key]
assert all(sha(Path(path))==value for path,value in prepared['dependencies'].items())
output=base/'evidence/PG34720-ssc434-aad5-unit-v1';unit=runs/'pg34720-ssc434-aad5-v1';assert not output.exists() and not unit.exists();output.mkdir();unit.mkdir();(unit/'tmp').mkdir();capture.SLOT=output
jdk=tc/'jdk-25.0.4/bin';console=tc/'junit-platform-console-standalone-1.13.4.jar';agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';session='PG34720-SSC434-AAD-ERASE-WHOLE5'
classpath=':'.join([str(work/'component'),str(work/'test-classes'),*prepared['dependencies']]);selected=sorted({case['classname'] for case in prepared['expectedCases']});assert len(selected)==2
command=[str(jdk/'java'),'-Djava.io.tmpdir='+str(unit/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.execution.parallel.enabled=false','-Djunit.jupiter.extensions.autodetection.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(unit/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(unit/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',classpath,*[argument for name in selected for argument in ['--select-class',name]],'--reports-dir',str(unit/'xml'),'--fail-if-no-tests','--details','summary']
begin=dict(producer=ref(Path(__file__).resolve()),source=unit_source,productionCoreMain='eaea0c45bc6df704f2e900825da4d00b109ac503',inputHashes=prepared['inputHashes'],physicalClassHashes=prepared['physicalClassHashes'],testClassHashes=prepared['testClassHashes'],dependencies=prepared['dependencies'],expectedCases=prepared['expectedCases'],expectedTests=5,newDefinitions=0,necessaryPriorDefinitions=5,selectedClasses=selected,session=session,oldExecCombined=False,prepare=ref(prepared_path),preflight=ref(admission_path),mainCompilationReusedExactCurrentSource=False,freshRootNullAwayCompileWithinSameGroup=True,rootNullAwayReusedExactUnchangedMainFromPriorQualifiedGroup=False,all182FullCoverageClaim=False,actualBackendOrHeldClassActions=0)
(output/'begin.json').open('x').write(json.dumps(begin,indent=2)+'\n')
stages={'unit':capture.step('unit',command,unit,timeout=180)}
if (unit/'jacoco.exec').is_file():
    for label,args in [('coverage',['report',str(unit/'jacoco.exec'),'--classfiles',str(work/'component'),'--xml',str(unit/'coverage.xml')]),('classinfo',['classinfo',str(work/'component')]),('execinfo',['execinfo',str(unit/'jacoco.exec')])]:stages[label]=capture.step(label,[str(jdk/'java'),'-jar',str(cli),*args],root)
actual=[]
for path in (unit/'xml').glob('TEST-*.xml'):
    for case in ET.parse(path).findall('testcase'):actual.append(dict(classname=case.get('classname'),name=case.get('name'),failure=case.find('failure') is not None,error=case.find('error') is not None,skipped=case.find('skipped') is not None))
failures=sum(case['failure'] for case in actual);errors=sum(case['error'] for case in actual);skipped=sum(case['skipped'] for case in actual)
matching=sorted((case['classname'],case['name']) for case in actual)==sorted((case['classname'],case['name']) for case in prepared['expectedCases'])
qualified=type(stages['unit']['actualExit']) is int and stages['unit']['actualExit']==0 and stages['unit']['timedOut'] is False and len(actual)==5 and matching and failures==errors==skipped==0 and len(stages)==4 and all(type(value['actualExit']) is int and value['actualExit']==0 and value['timedOut'] is False for value in stages.values())
manifest=dict(actualExit=0 if qualified else 1,actualUnitExit=stages['unit']['actualExit'],source=unit_source,productionCoreMain=begin['productionCoreMain'],begin=begin,stages=stages,cases=actual,tests=len(actual),newDefinitions=0,necessaryPriorDefinitions=5,failures=failures,errors=errors,skipped=skipped,exactExpectedCases=matching,unitResultQualified=qualified,oldExecCombined=False,whole451Accepted=False,formalUpdated=False,whole182CoverageAccepted=False)
(output/'manifest.json').open('x').write(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({key:manifest[key] for key in ['actualExit','actualUnitExit','tests','newDefinitions','necessaryPriorDefinitions','failures','errors','skipped','exactExpectedCases','unitResultQualified']}));raise SystemExit(0 if qualified else 1)
