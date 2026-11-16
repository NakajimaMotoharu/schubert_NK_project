"""Ordinary whole Test preparation for the previously qualified public provider boundary; no PT."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
cp=b/'evidence/PG36956-backup-path-four-main-compile-v1/manifest.json';root=load(cp)
assert root['actualExit']==0 and root['sourceCore']=='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9'
prefix='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/'
tests={prefix+'FixedNativeCoverageCheckpointTest.java':12,prefix+'CheckpointFatalBoundaryTest.java':3}
old=load(b/'evidence/provisional/PG17624-checkpoint-public-provider-twelve-independent-v1/manifest.json')
equivalence=load(b/'evidence/PG36974-checkpoint-original12-style-before-v1/equivalence.json')
assert old['actualExit']==equivalence['actualExit']==0 and equivalence['inverseWholeByteExact']
assert old['originalTestSourceHashes'][equivalence['testPath']]==equivalence['testShaBefore']
assert sha(r/equivalence['testPath'])==equivalence['testShaAfter']
for p,count in tests.items():
    text=(r/p).read_text();assert len(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text))==count
    assert not any(x in text for x in ['ProcessBuilder','DriverManager','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','NativeCoveragePrivateFile.','Runtime.getRuntime','System.setProperty','Class.forName'])
    assert '@TempDir' not in text and '@BeforeAll' not in text
work=r.parent/'pgpt-runs/PG379/pg36976-checkpoint15-prepare-v2';out=b/'evidence/PG36976-checkpoint15-prepare-static-v2'
assert not work.exists() and not out.exists();work.mkdir();out.mkdir()
component=work/'component';component.mkdir();physical={};main_inputs={}
for module in ['storage','bootstrap']:
    folder=Path(root['cwd'])/('src/schubert-nk-'+module)/'target/classes'
    for n,h in root['physicalClassHashes'][module].items():
        assert sha(folder/n)==h and n not in physical
        target=component/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(folder/n,target);physical[n]=h
    main_inputs.update({p:h for p,h in root['inputHashes'].items() if p.startswith('src/schubert-nk-'+module+'/')})
assert len(physical)==280
assert not any(Path(n).stem.split('$')[0] in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'] for n in physical)
assert all(sha(r/p)==h for p,h in main_inputs.items())
sources=[];test_hashes={}
for p in tests:
    f=work/'test-source'/p;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/p,f);sources.append(f);test_hashes[p]=sha(r/p)
test_classes=work/'test-classes';test_classes.mkdir()
deps=[tc/'junit-platform-console-standalone-1.13.4.jar',tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',tc/'m2/repository/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar']
classpath=':'.join(map(str,[component,*deps]));jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015'
libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]
rules=r/'tools/quality/static';listing=out/'sources.txt';listing.write_text(''.join(str(r/p)+'\n' for p in tests))
tool_inputs=[*deps,*libs,sg/'checkstyle-14.3.0-all.jar',tc/'google-java-format-1.36.1-all-deps.jar',rules/'pmd.xml',rules/'checkstyle.xml']
pins={str(p):sha(p) for p in tool_inputs}
stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
commands={
 'format':[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(r/p) for p in tests]],
 'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],
 'test-compile':[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(test_classes),*map(str,sources)],
 'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+classpath,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]}
stages={}
for name,command in commands.items():
    stages[name]=stage.step(name,command,work,timeout=120)
    assert not stages[name]['timedOut'] and stages[name]['actualExit'] in ([0,4] if name=='pmd' else [0]),'preserve failed stage before proceeding'
raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
    tag=node.tag.rsplit('}',1)[-1]
    if tag in ['error','configerror']:errors.append(dict(node.attrib))
    if tag=='file':
        for item in node:
            if item.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**item.attrib,message=(item.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error')
assert all(sha(r/p)==h for p,h in test_hashes.items()) and all(sha(Path(p))==h for p,h in pins.items())
assert all(sha(component/p)==h for p,h in physical.items())
(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,source=root['sourceCore'],sourceCore=root['sourceCore'],
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rootCompile=ref(cp),mainInputHashes=main_inputs,
    testSourceHashes=test_hashes,physicalClassHashes=physical,testPhysicalHashes={str(p.relative_to(test_classes)):sha(p) for p in test_classes.rglob('*.class')},
    classpath=classpath,work=str(work),toolDependencyHashes=pins,stages=stages,rawFindings=raw,processingErrors=errors,
    expectedTests=15,wholeTestSourceCounts=tests,productTestsExecuted=0,normalPrior12NotReusedAsCurrent=True,
    requiredBeforeRun='all static findings individually reviewed, source frozen at full Unit commit, fresh quota admission',formalUpdated=False),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,mainPhysical=280,testSources=2,expectedTests=15,raw=len(raw),processingErrors=0,productTestsExecuted=0)))
