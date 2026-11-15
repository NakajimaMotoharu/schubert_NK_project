"""Reuse exact approved Main bytecode and compile whole8 Test sources; no backend operations."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
import pg9666_pagination_static as capture
import pgpt_closed_host_profile as policy

root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001';tc=root.parent/'toolchain';runs=root.parent/'pgpt-runs/PG379'
output=base/'evidence/PG33730-readwire58-prepare-v1';work=runs/'pg33730-readwire58-v1';assert not output.exists() and not work.exists()
load=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();ref=lambda path:dict(path=str(path.relative_to(root)),sha256=sha(path))
postpath=base/'evidence/PG27836-read-wire-normal40-independent-v1/manifest.json';post=load(postpath);assert post['actualExit']==0 and post['tests']==40
oldpath=base/'evidence/PG27824-read-wire-normal40-v1/manifest.json';old=load(oldpath);preflight_path=base/'evidence/PG27828-read-wire-normal40-preflight-v1/manifest.json';preflight=load(preflight_path)
assert preflight['actualExit']==0 and preflight['staticApplicable']==0 and preflight['rootCompilerUnchanged']
assert all(sha(root/path)==value for path,value in post['inputHashes'].items())
names=sorted(post['physicalClassHashes']);assert len(names)==194
for name in names:policy.relative_name(name)
origin=runs/'pg27824-read-wire-normal40-v1/component';assert {name:sha(origin/name) for name in names}==post['physicalClassHashes']
dependencies=post['dependencies'];assert len(dependencies)==4
proto=load(base/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json')
approved={Path(proto['jar']['path']).name,'jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar','jakarta.jms-api-3.1.0.jar'}
assert {Path(path).name for path in dependencies}==approved
assert all(not any(word in path.lower() for word in ['postgres','artemis','hikari','jna','jnr']) for path in dependencies)
assert all(sha(Path(path))==value for path,value in dependencies.items())
testdir='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/'
extra=[testdir+name+'.java' for name in ['JmsRequestReplyClientTest','ReplyCorrelationRegistryTest','ProtectedReadReasonContractTest']]
tests=old['apiTestSources']+extra;assert len(tests)==8 and len(set(tests))==8
expected=[];counts=[8,8,8,8,8,10,7,1]
for path,count in zip(tests,counts):
    text=(root/path).read_text()
    assert not any(marker in text for marker in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','@BeforeAll','@TempDir','ProcessBuilder','DriverManager','DataSource','java.nio.file','Class.forName'])
    methods=re.findall(r'@Test\s*(?:@Timeout\([^\n]+\)\s*)?void (\w+)\s*\(',text);assert len(methods)==count
    expected.extend(dict(classname=path.split('/src/test/java/')[1][:-5].replace('/','.'),name=method+'()') for method in methods)
assert len(expected)==58
inputs=dict(post['inputHashes']);inputs.update({path:sha(root/path) for path in extra});assert len(inputs)==189
output.mkdir();work.mkdir();(work/'component').mkdir();(work/'test-classes').mkdir()
for name in names:
    destination=work/'component'/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin/name,destination);assert sha(destination)==post['physicalClassHashes'][name]
capture.SLOT=output;jdk=tc/'jdk-25.0.4/bin';gates=tc/'static-gates-20261015'
classpath=':'.join([str(work/'component'),*dependencies])
stages={}
stages['test-compile']=capture.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',classpath,'-d',str(work/'test-classes'),*[str(root/path) for path in tests]],root)
assert stages['test-compile']['actualExit']==0 and not stages['test-compile']['timedOut']
listing=output/'sources.txt';listing.write_text(''.join(str(root/path)+'\n' for path in old['apiMainSources']+tests))
stages['format']=capture.step('format',[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--dry-run','--set-exit-if-changed','--skip-reflowing-long-strings',*[str(root/path) for path in old['apiMainSources']+tests]],root)
stages['checkstyle']=capture.step('checkstyle',[str(jdk/'java'),'-jar',str(gates/'checkstyle-14.3.0-all.jar'),'-c',str(root/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(output/'checkstyle.xml'),'@'+str(listing)],root)
pmd_tools=[gates/'record-fix-v1/pmd-record-1298.jar',*sorted((gates/'pmd-bin-7.28.0/lib').glob('*.jar'))]
stages['pmd']=capture.step('pmd',[str(jdk/'java'),'-cp',':'.join(map(str,pmd_tools)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(root/'tools/quality/static/pmd.xml'),'--use-version','java-25','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+classpath,'--no-cache','--format','xml','--report-file',str(output/'pmd.xml')],root)
for label in ['format','checkstyle']:assert stages[label]['actualExit']==0 and not stages[label]['timedOut']
assert stages['pmd']['actualExit'] in [0,4] and not stages['pmd']['timedOut']
assert not ET.parse(output/'checkstyle.xml').findall('.//error')
parsed=ET.parse(output/'pmd.xml').getroot();errors=[dict(node.attrib) for node in parsed.iter() if node.tag.rpartition('}')[2] in ['error','configerror']]
findings=[dict(path=node.get('name'),rule=violation.get('rule'),line=violation.get('beginline'),message=(violation.text or '').strip()) for node in parsed if node.tag.rpartition('}')[2]=='file' for violation in node if violation.tag.rpartition('}')[2]=='violation'];assert not errors
test_hashes={}
for path in (work/'test-classes').rglob('*.class'):
    name=str(path.relative_to(work/'test-classes'));policy.relative_name(name);test_hashes[name]=sha(path)
assert all(sha(root/path)==value for path,value in inputs.items())
manifest=dict(actualExit=0,inputHashes=inputs,mainSources=old['apiMainSources'],testSources=tests,expectedCases=expected,expectedTests=58,newDefinitions=1,necessaryPriorDefinitions=57,dependencies=dependencies,physicalClassHashes=post['physicalClassHashes'],testClassHashes=test_hashes,stages=stages,rawFindings=findings,processingErrors=errors,checkstyleFindings=0,originalMainPrepare=ref(oldpath),originalMainStaticPreflight=ref(preflight_path),originalIndependentPost=ref(postpath),mainCompilationReusedExact186CurrentInputs=True,mainNullAwayAndSpotbugsReusedExactSourceAndClass=True,mainRebuilds=0,applicationTestsExecuted=0,actualBackendOrHeldClassActions=0,all194FullCoverageStillRequiredSeparately=True,newAcceptance=0,whole451Accepted=False,formalUpdated=False)
(output/'manifest.json').open('x').write(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,expectedTests=58,newDefinitions=1,testClasses=len(test_hashes),stageExits={name:value['actualExit'] for name,value in stages.items()},rawFindings=len(findings),rawSites=[dict(file=Path(value['path']).name,rule=value['rule'],line=value['line']) for value in findings])))
