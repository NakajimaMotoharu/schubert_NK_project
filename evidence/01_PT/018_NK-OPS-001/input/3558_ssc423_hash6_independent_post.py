"""Independent whole13 XML, exact current183 CRC/init and five API source scope proof."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import pgpt_closed_host_profile as policy

root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001';runs=root.parent/'pgpt-runs/PG379';work=runs/'pg33885-ssc423-hash6-v2';unit=runs/'pg33900-ssc423-hash6-v1';run=base/'evidence/PG33900-ssc423-hash6-unit-v1';output=base/'evidence/PG33902-ssc423-hash6-independent-v1';assert not output.exists()
load=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();ref=lambda path:dict(path=str(path.relative_to(root)),sha256=sha(path))
assert len(sys.argv)==2
manifest=load(run/'manifest.json');begin=manifest['begin'];assert begin['source']==sys.argv[1] and begin['productionCoreMain']=='5a5d852e5f9c98755abd20f982331c23819605d7'
assert (manifest['actualExit'],manifest['actualUnitExit'],manifest['tests'],manifest['failures'],manifest['errors'],manifest['skipped'])==(0,0,6,0,0,0)
for path,value in begin['inputHashes'].items():assert sha(root/path)==value==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+path])).hexdigest()
for path,value in begin['dependencies'].items():assert sha(Path(path))==value
admission_path=root/begin['preflight']['path'];admission=load(admission_path);assert sha(admission_path)==begin['preflight']['sha256'] and admission['actualExit']==0 and admission['inputHashes']==begin['inputHashes']
assert all(admission[key]==0 for key in ['staticApplicable','unclassified','processingErrors','checkstyle']) and admission['rootNullAwayFresh']
for label,value in manifest['stages'].items():
    assert type(value['actualExit']) is int and value['actualExit']==0 and value['timedOut'] is False and value==load(run/(label+'-exit.safe.json'))
    for stream in ['stdout','stderr']:assert sha(run/(label+'.'+stream))==value[stream+'Sha256']
command=manifest['stages']['unit']['command'];selected=begin['selectedClasses'];assert len(selected)==len(set(selected))==1 and command.count('--select-class')==1 and '--select-method' not in command and '--scan-classpath' not in command
assert not any(marker in str(command) for marker in ['schubert-nk-web-0.1','schubert-nk-api-0.1','artemis','postgres','enable-native-access','excludes='])
expected={(case['classname'],case['name']) for case in begin['expectedCases']};actual=[];environment={};xml_paths=sorted((unit/'xml').glob('TEST-*.xml'))
for path in xml_paths:
    tree=ET.parse(path).getroot();assert not any(tree.findall('.//'+tag) for tag in ['failure','error','skipped'])
    actual.extend((case.get('classname'),case.get('name')) for case in tree.findall('testcase'))
    environment.update({prop.get('name'):prop.get('value') for prop in tree.findall('./properties/property') if prop.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(actual)==len(set(actual))==6 and set(actual)==expected
summary=(run/'unit.stdout').read_text()
for text in ['6 tests found','6 tests started','6 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in summary
prepared_path=root/begin['prepare']['path'];prepared=load(prepared_path);assert sha(prepared_path)==begin['prepare']['sha256']
for name in list(begin['physicalClassHashes'])+list(begin['testClassHashes']):policy.relative_name(name)
physical={name:sha(work/'component'/name) for name in begin['physicalClassHashes']};assert physical==begin['physicalClassHashes'] and len(physical)==180
assert prepared['testClassHashes']=={name:sha(work/'test-classes'/name) for name in begin['testClassHashes']}
test_names={name.removesuffix('.class') for name in prepared['testClassHashes']}
helper=base/'input/1415_manifest_current_independent_post.py';nodes=[node for node in ast.parse(helper.read_text()).body if isinstance(node,ast.FunctionDef) and node.name in ['crc64','code_count']];assert len(nodes)==2
namespace={'struct':struct};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),namespace)
ids={name.removesuffix('.class'):namespace['crc64']((work/'component'/name).read_bytes()) for name in physical}
methods={name.removesuffix('.class'):namespace['code_count']((work/'component'/name).read_bytes()) for name in physical};no_code={name for name,count in methods.items() if count==0}
proto=load(base/'evidence/PG26312-protocol-unicode-full130-independent-v1/manifest.json');switchmaps=set(proto['defaultSyntheticSwitchmaps']);assert len(switchmaps)==4 and all(methods[name]>0 for name in switchmaps)
info={name:dict(crc=crc,instructions=int(instructions)) for instructions,branch,line,method,complexity,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(run/'classinfo.stdout').read_text(),re.M)}
classinfo_crc={name:value['crc'] for name,value in info.items()};analyzed={name for name,value in info.items() if value['instructions']>0};assert analyzed==set(ids)-no_code-switchmaps
missing=set(ids)-set(classinfo_crc);assert all(name.endswith('/package-info') and name in no_code for name in missing);assert all(ids[name]==crc for name,crc in classinfo_crc.items())
execinfo=(run/'execinfo.stdout').read_text();assert execinfo.count('Session "')==1 and 'Session "PG33900-SSC423-CONTEXT-HASH-WHOLE6"' in execinfo
probes={name:(crc,int(hit),int(total)) for crc,hit,total,name in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',execinfo,re.M)}
observed={name for name in probes if name.startswith('dev/codex/schubert/nk/') and name not in test_names};assert observed<=analyzed|switchmaps and all(probes[name][0]==ids[name] and probes[name][1]>0 for name in observed)
initialized={name for name in re.findall(r"Initializing '([^']+)'",(unit/'class-init.log').read_text()) if name.startswith('dev/codex/schubert/nk/') and not any(name==test or name.startswith(test+'$') for test in test_names)}
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(name.endswith('/'+item) for name in initialized for item in held)
real=initialized&set(ids);generated=initialized-set(ids);assert real-observed<=no_code and observed<=real
def owner(name):
    match=re.fullmatch(r'(dev/codex/schubert/nk/[^+]+)\$\$Lambda\+0x[0-9a-f]+',name)
    return match.group(1) if match and match.group(1) in ids else None
bindings={name:owner(name) for name in generated};assert all(bindings.values())
report=ET.parse(unit/'coverage.xml').getroot();classes={node.get('name'):node for node in report.findall('.//class')};assert set(classes)==set(classinfo_crc)
coverage={node.get('type'):dict(covered=int(node.get('covered')),missed=int(node.get('missed'))) for node in report.findall('counter')}
for kind,value in coverage.items():
    for metric in ['covered','missed']:assert sum(int(counter.get(metric)) for cls in classes.values() for counter in cls.findall('counter') if counter.get('type')==kind)==value[metric]
uncovered={name:{counter.get('type'):int(counter.get('missed')) for counter in cls.findall('counter') if int(counter.get('missed'))>0} for name,cls in classes.items() if any(int(counter.get('missed'))>0 for counter in cls.findall('counter'))}
web_names={name for name in ids if '/api/' in name};assert web_names=={name[:-6] for name in prepared['mainClassHashes']} and len(web_names)==4
own_counter={kind:dict(covered=sum(int(counter.get('covered')) for name in web_names&set(classes) for counter in classes[name].findall('counter') if counter.get('type')==kind),missed=sum(int(counter.get('missed')) for name in web_names&set(classes) for counter in classes[name].findall('counter') if counter.get('type')==kind)) for kind in coverage}
own_default100=all(own_counter[kind]['missed']==0 and (own_counter[kind]['covered']>0 or kind=='BRANCH') for kind in ['LINE','METHOD','CLASS','BRANCH'])
targets=admission['declaredTargets'];assert len(targets)==2 and set(targets)<web_names
assert set(targets)-set(classes)<=no_code
report_targets=set(targets)&set(classes)
target_counter={kind:dict(covered=sum(int(counter.get('covered')) for name in report_targets for counter in classes[name].findall('counter') if counter.get('type')==kind),missed=sum(int(counter.get('missed')) for name in report_targets for counter in classes[name].findall('counter') if counter.get('type')==kind)) for kind in coverage}
target_default100=all(target_counter[kind]['missed']==0 and (target_counter[kind]['covered']>0 or kind=='BRANCH') for kind in ['LINE','METHOD','CLASS','BRANCH']);assert target_default100
assert uncovered and not all(value['missed']==0 for value in coverage.values())
output.mkdir();files={};raw_xml_pins={}
for source,prefix in [(run,'unit-'),(unit,'original-')]:
    for path in source.iterdir():
        if not path.is_file():continue
        assert path.suffix!='.class';name='jacoco.exec' if path.name=='jacoco.exec' else prefix+('class-init.stdout' if path.name=='class-init.log' else path.name);assert name not in files;shutil.copyfile(path,output/name);files[name]=sha(output/name)
for path in xml_paths:
    raw_xml_pins[path.name]=sha(path);tree=ET.parse(path);document=tree.getroot()
    for properties in document.findall('properties'):
        for prop in list(properties):
            if prop.get('name') not in environment:properties.remove(prop)
    for tag in ['system-out','system-err']:
        for node in document.findall(tag):document.remove(node)
    name='sanitized-'+path.name;tree.write(output/name,encoding='utf-8',xml_declaration=True);files[name]=sha(output/name)
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=begin['source'],productionCoreMain=begin['productionCoreMain'],run=begin['session'],tests=6,newTestDefinitions=3,necessaryPriorDefinitions=3,physicalClasses=180,positiveMainCrc=len(observed),coverage=coverage,uncoveredFullSourceClasses=uncovered,wholeScopeFour100=False,own1HashSource2CodeRequiredCountersQualified=own_default100,ownApiDefaultCounters=own_counter,targetHashRequiredCountersQualified=target_default100,targetHashCounters=target_counter,declaredTargets=targets,ownHashSourceScopeDeclaredBeforeRun=True,branchNaturallyZeroNotArtificial100=True,ownNaturalNoCode=sorted(web_names&no_code),ownNaturalBranch0NotArtificial100=True,rawSupplementRequired=True,physicalClassHashes=physical,classIds=ids,actualJvmCodeMethodCounts=methods,naturalNoCodeClasses=sorted(no_code),defaultStandardFilteredSwitchMaps=sorted(switchmaps),naturallyOmittedPackageAnnotations=sorted(missing),hiddenJvmAdapters=bindings,manualCoverageExclusions=[],oldExecCombined=False,preflight=ref(admission_path),inputHashes=begin['inputHashes'],dependencies=begin['dependencies'],environment=environment,staticApplicable=0,processingErrors=0,unclassified=0,actualBackendNativeFsRootOrHeldClassActions=0,heldFixtureExtractedOrSubstituted=False,originalXmlHashes=raw_xml_pins,xmlPropertiesAndSystemOutNotExportedExceptFiveNonsecretEnvironment=True,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,independentCodeHelper=ref(helper),verifier=ref(Path(__file__).resolve()))
(output/'manifest.json').open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=6,newDefinitions=3,physical=180,positiveCrc=len(observed),ownDefault=own_counter,ownApiSourceFour100=own_default100,whole180Accepted=False)))
