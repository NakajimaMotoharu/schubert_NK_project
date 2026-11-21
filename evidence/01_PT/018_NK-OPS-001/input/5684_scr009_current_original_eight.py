from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import mkdtemp
from xml.etree import ElementTree as ET

ROOT = Path.cwd()
OUT = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence'
RUN = 'PG41454-scr009-current-original-eight-v1'
STATE = ROOT.parent/'pgpt-runs/PG379'/RUN
TOOLS = ROOT.parent/'toolchain'
JDK = TOOLS/'jdk-25.0.4/bin'
JAVA, JAVAC = JDK/'java', JDK/'javac'
CACHE = TOOLS/'m2/repository'
TEST_NAME = 'dev.codex.schubert.nk.web.view.AnimationViewModelTest'
WEB = Path('src/schubert-nk-web/src')
NS = Path('dev/codex/schubert/nk/web')
PMO = next((ROOT/'documents/400_PGPT/470_PMO').glob('601_*'))

def load(path):
    return json.loads(path.read_bytes())

def pin(path):
    return {'path':str(path),'sha256':sha256(path.read_bytes()).hexdigest()}

def find(run):
    return next(ROOT.glob('evidence/01_PT/*/evidence/'+run+'-*/manifest.json'))

def write(path,data):
    with path.open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write('\n')

def checked_path(path,digest):
    assert path.is_file() and pin(path)['sha256']==digest, path
    return path

def git(*args):
    return subprocess.check_output(['git',*args],timeout=15)

def run(label,argv):
    result=subprocess.run([str(a) for a in argv],timeout=60,capture_output=True, env={**os.environ,'LC_ALL':'C.UTF-8','TZ':'Asia/Tokyo'})
    stdout, stderr = STATE/(label+'.stdout'), STATE/(label+'.stderr')
    stdout.write_bytes(result.stdout)
    stderr.write_bytes(result.stderr)
    outcome=dict(argv=[str(a) for a in argv],exit=result.returncode,stdout=pin(stdout),stderr=pin(stderr))
    write(STATE/(label+'-terminal.json'),outcome)
    return result

def current_quota_before_product():
    # The group quota was obtained through the application immediately before this short execution.
    q=load(next(PMO.glob('1837_*')))['quota']
    assert q['ordinaryUsageAllowed'] is True and q['primary']['remainingPercent'] > 10
    assert q['secondary'] is None or q['secondary']['remainingPercent'] > 10
    return q

def main():
    context=load(next(PMO.glob('1837_*')))['values']
    quota=current_quota_before_product()
    assert git('rev-parse','HEAD').decode().strip()==context['source']
    assert shutil.disk_usage('/dev/shm').free >= 100*1024*1024
    source_fixture=WEB/'test/java'/NS/'view/AnimationViewModelTest.java'
    ordinary_names=('view/AnimationListViewModel','view/AnimationMenuViewModel','view/TopBarViewModel','session/SessionPrincipal')
    sources=[WEB/'main/java'/NS/(x+'.java') for x in ordinary_names]+[source_fixture]
    inputs={}
    for path in sources:
        content=(ROOT/path).read_bytes()
        assert content==git('show',f"{context['source']}:{path}")
        inputs[str(path)]=pin(path)['sha256']
    original=find('PG24476')
    original_receipt=load(original)
    old_run=original.parent/'original-manifest.json'
    assert pin(old_run)['sha256']==original_receipt['files'][old_run.name]
    original=load(old_run)
    originals={row['name'] for row in original['cases'] if row['classname']==TEST_NAME}
    assert len(originals)==8
    approved_deps=original['begin']['dependencies']
    dependencies=[]
    for file,digest in approved_deps.items():
        p=Path(file)
        if p.name.startswith('schubert-nk-'):
            assert p.name.startswith(('schubert-nk-web-','schubert-nk-protocol-'))
            continue
        assert p.is_relative_to(TOOLS) and p.suffix=='.jar'
        dependencies.append(checked_path(p,digest))
    package=find('PG41322')
    packaging=load(package)['packagingProof']['artifacts']['protocol']
    protocol=packaging['artifact']
    protocol_path=checked_path(Path(protocol['path']),protocol['sha256'])
    assert git('diff','--name-only',packaging['archiveSource'],context['productionCoreMain'],'--',
               'pom.xml','src/schubert-nk-protocol')==b''
    console=checked_path(TOOLS/'junit-platform-console-standalone-1.13.4.jar',original['begin']['consoleSha256'])
    agent=CACHE/'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    proven_agent=load(find('PG38002'))['measurementAgentSha256']
    checked_path(agent,proven_agent)
    analyzer_source=ROOT/'tools/quality/jacoco/UnfilteredCodeMeasurement.java'
    assert analyzer_source.read_bytes()==git('show',f"{context['source']}:{analyzer_source.relative_to(ROOT)}")
    reference=load(find('PG41304'))
    analysis_deps=[Path(p) for p in reference['tools'][0]['argv'][5].split(os.pathsep)]
    assert len(analysis_deps)==4 and all(p.is_file() and p.is_relative_to(TOOLS) for p in analysis_deps)
    cp=lambda seq:os.pathsep.join(map(str,seq))
    STATE.mkdir()
    base=Path(mkdtemp(prefix='pgpt-scr009-ordinary8-',dir='/dev/shm'))
    classes, analyzer = base/'classes',base/'analyzer'
    classes.mkdir();analyzer.mkdir()
    write(STATE/'begin.json',dict(run=RUN,source=context['source'],productionCoreMain=context['productionCoreMain'],
        atUTC=datetime.now(timezone.utc).isoformat(),scope=sources_as_strings(sources),quota=quota,scratch=str(base),
        expectedCases=sorted(originals),artifact=protocol,sourceInputs=inputs,dependencies=[pin(p) for p in (protocol_path,*dependencies,console,agent,*analysis_deps)],
        excludedProductArchives=['old web jar','old protocol jar']))
    cp_compile=cp([protocol_path,*dependencies,console])
    product=run('compile',[JAVAC,'--release','25','-Xlint:all','-Werror','-proc:none','-implicit:none',
        '-encoding','UTF-8','-cp',cp_compile,'-d',classes,*sources])
    assert product.returncode==0
    extract=run('analyzer-compile',[JAVAC,'--release','25','-proc:none','-cp',cp(analysis_deps),'-d',analyzer,analyzer_source])
    assert extract.returncode==0
    files=sorted(classes.rglob('*.class'))
    assert all(any(f.relative_to(classes).as_posix().startswith((NS/x).as_posix()) for x in (*ordinary_names,'view/AnimationViewModelTest')) for f in files)
    publish_candidates=[path for path in files if 'ViewModelTest' not in path.name]
    intended=sorted(path.relative_to(classes).as_posix().removesuffix('.class') for path in publish_candidates)
    assert len(publish_candidates)==6
    xml=STATE/'xml'
    exec_file=STATE/'unit.exec'
    junit=run('unit',[JAVA,'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
        f'-javaagent:{agent}=destfile={exec_file},append=false,sessionid={RUN}',
        '-cp',cp([classes,protocol_path,*dependencies,console]),'org.junit.platform.console.ConsoleLauncher','execute',
        '--disable-banner','--disable-ansi-colors','--details','summary','--fail-if-no-tests','--include-engine','junit-jupiter',
        '--select-class',TEST_NAME,'--reports-dir',xml])
    report=xml/'TEST-junit-jupiter.xml'
    root=ET.parse(report).getroot()
    rows=[dict(classname=row.attrib['classname'],name=row.attrib['name'],
        outcome=next((tag.upper() for tag in ('failure','error','skipped') if row.find(tag) is not None),'PASS'))
        for row in root.findall('testcase')]
    assert len(rows)==8 and all(row['classname']==TEST_NAME for row in rows)
    assert {row['name'] for row in rows}==originals
    assert junit.returncode==0 and all(row['outcome']=='PASS' for row in rows)
    measurement=run('coverage',[JAVA,'-cp',cp([analyzer,*analysis_deps]),
        'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement','--strict-original-exec','--line-deficits',
        exec_file,*publish_candidates])
    assert measurement.returncode==0
    sys.path.insert(0,str(ROOT/'tools/quality'))
    from jacoco_readonly_exec_subset import decode
    actual_exec=decode(exec_file.read_bytes(),set(intended),strict_class_names=True)
    assert len(actual_exec['sessions'])==1 and actual_exec['sessions'][0]['labelBytesHex']==RUN.encode().hex()
    counters={}
    for line in measurement.stdout.decode().splitlines():
        cols=line.split('\t')
        if cols[0]=='CLASS':
            name,crc,seen=cols[1:4]
            assert seen=='true' and int(crc,16)==int(actual_exec['classes'][name]['crc64'],16)
            counters[name]={part[0]:dict(missed=int(part[1]),covered=int(part[2]))
                            for value in cols[6:] for part in (value.split(':'),)}
    assert set(counters)==set(intended)
    outcome=OUT/RUN
    outcome.mkdir()
    raw=outcome/'unfiltered.tsv'
    raw.write_bytes(measurement.stdout)
    write(outcome/'manifest.json',dict(run=RUN,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
      source=context['source'],productionCoreMain=context['productionCoreMain'],cases=rows,tests=len(rows),firstSuccess=True,
      failures=0,errors=0,skipped=0,notRun=0,newDefinitions=0,sourceRequalification=8,originalResubmittedOverclaimCase=0,
      runtimeFixtures='original whole JUnit fixture, synthetic DOM, owned finite executor',
      sourceInputs=inputs,compiledClasses={p.relative_to(classes).as_posix():pin(p)['sha256'] for p in files},
      inventory=pin(STATE/'begin.json'),commandAndActualExit=[pin(STATE/(step+'-terminal.json')) for step in ('compile','analyzer-compile','unit','coverage')],
      originalXml=pin(report),originalExec=pin(exec_file),raw=pin(raw),counters=counters,
      allRawPhysicalClassCount=len(counters),sameSingleSessionVerified=True,coverageUnion=False,
      actualRealEnvironmentActions=0,formalDelta=0,whole451=False))
    print(len(rows),{name:{k:counters[name][k]['missed'] for k in ('LINE','METHOD','CLASS','BRANCH')} for name in sorted(counters)})

def sources_as_strings(sources):
    return [str(path) for path in sources]

if __name__=='__main__':
    main()
