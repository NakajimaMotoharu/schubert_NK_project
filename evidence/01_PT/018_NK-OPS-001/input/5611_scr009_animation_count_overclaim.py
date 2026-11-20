"""Bounded Animation projection unit case using a current, admitted six-dependency closure."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import runpy
import shutil
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


H = runpy.run_path(str(Path(__file__).with_name('5609_scr012_count_underclaim.py')))
BIN, OPS, WEB, PROTO = (H[k] for k in ('BIN','OPS','WEB','PROTO'))
read, pin, sha, check, successful_case = (
    H[k] for k in ('read','pin','sha','check','successful_case'))
PROJECTION = 'dev/codex/schubert/nk/web/view/AnimationListViewModel'
TESTTYPE = 'dev.codex.schubert.nk.web.view.AnimationListCountBoundaryTest'
TEST = WEB/'test/java'/Path(TESTTYPE.replace('.', '/')+'.java')
MAIN = WEB/'main/java'/Path(PROJECTION+'.java')
RUN = 'PG41182-scr009-animation-overclaimed-count-v1'


def main():
    record, = Path('documents/400_PGPT/470_PMO').glob('601_*/1607_*.json')
    plan = read(record)['values']
    assert all(pin(Path(ref['path'])) == ref for ref in plan['oracleReferences'])
    assert shutil.disk_usage('/dev/shm').free > 32 * 1024**2 and shutil.disk_usage('.').free > 64 * 1024**2
    prep, old = [Path(row['path']) for row in plan['oracleReferences'][1:3]]
    actual = read(old.with_name('original-manifest.json'))
    assert pin(old.with_name('original-manifest.json'))['sha256'] == read(old)['files']['original-manifest.json']
    assert actual['actualExit']==actual['failures']==actual['errors']==actual['skipped']==0
    case, = [c for c in actual['cases'] if c['name']=='web232OvaAndBounds()']
    assert not any(case[k] for k in ('failure','error','skipped'))
    graph = read(prep)['sourceGraphHashes']
    sources = [MAIN, *(WEB/'main/java/dev/codex/schubert/nk/web'/name for name in (
        'view/TopBarViewModel.java','session/SessionPrincipal.java'))]
    sources += [(PROTO/'dev/codex/schubert/nk/protocol')/name for name in (
        'header/AuthenticationContext.java','layout/semantic/UserRole.java',
        'layout/semantic/AnimationListCategory.java','layout/semantic/AnimationCategory.java',
        'layout/media/AnimationRecord.java','layout/media/AnimationListResponseData.java')]
    for path in sources:
        original = subprocess.check_output(['git','show',f'{plan["productionCoreMain"]}:{path}'],timeout=15)
        assert sha(original)==graph[str(path)]==pin(path)['sha256']
    deps_source, = OPS.glob('PG37996-*/manifest.json')
    filename = ('current-protocol176.jar','jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar',
                'qualified-web-safe18.jar','spring-core-7.0.9.jar','spring-web-7.0.9.jar')
    all_deps = read(deps_source)['dependencies']
    deps = [Path(path) for path in all_deps if Path(path).name in filename]
    assert sorted(p.name for p in deps)==sorted(filename)
    assert all(pin(p)['sha256']==all_deps[str(p)] for p in deps)
    unit_prior, = OPS.glob('PG38002-*/manifest.json')
    prior = read(unit_prior)
    agent_flag, = [arg for arg in prior['command'] if arg.startswith('-javaagent:')]
    agent = Path(agent_flag.split('=',1)[0].removeprefix('-javaagent:'))
    assert pin(agent)['sha256']==prior['measurementAgentSha256']
    cli = Path('../toolchain/org.jacoco.cli-0.8.15-nodeps.jar').resolve()
    static = Path('../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar').resolve()
    stages = {}
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-scr009-count-') as root:
        classes = Path(root)/'classes'
        classes.mkdir()
        classpath = os.pathsep.join(map(str,[classes,*deps]))
        formatter = Path('../toolchain/google-java-format-1.36.1-all-deps.jar').resolve()
        stages['format'], fmt = check([BIN/'java','-jar',formatter,'--dry-run','--set-exit-if-changed',TEST])
        stages['style'], style = check([BIN/'java','-jar',static,'-c','tools/quality/static/checkstyle.xml','-f','xml',TEST])
        assert fmt.returncode==style.returncode==0 and not ET.fromstring(style.stdout).findall('.//error')
        stages['compile'], compilation = check([BIN/'javac','--release','25','-Xlint:all','-Werror','-proc:none',
                                                '-cp',classpath,'-d',classes,MAIN,TEST])
        assert compilation.returncode==0,compilation.stderr
        locations = [classes/(PROJECTION+suffix+'.class') for suffix in ('','$Row','$Video')]
        stages['crc'], info = check([BIN/'java','-jar',cli,'classinfo',*locations])
        assert info.returncode==0,info.stderr
        class_crcs = dict((b,a) for a,b in re.findall(r'(?m)^.*class 0x([0-9a-f]+) (\S+)\s*$',info.stdout.decode()))
        assert set(class_crcs)=={PROJECTION+suffix for suffix in ('','$Row','$Video')}
        old_info = old.with_name('classinfo.stdout')
        assert pin(old_info)['sha256']==read(old)['files']['classinfo.stdout']
        originals = dict((b,a) for a,b in re.findall(r'(?m)^.*class 0x([0-9a-f]+) (\S+)\s*$',old_info.read_text()))
        same_earlier_crc = {name:crc==originals[name] for name,crc in class_crcs.items()}
        store = (Path('../pgpt-runs/PG379')/RUN).resolve()
        store.mkdir()
        original_exec, xml = store/'unit.exec', store/'xml'
        stages['junit'], junit = check([BIN/'java','-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
            f'-javaagent:{agent}=destfile={original_exec},append=false,sessionid={RUN}',
            '-cp',classpath,'org.junit.platform.console.ConsoleLauncher','execute','--disable-banner',
            '--details=summary','--fail-if-no-tests','--reports-dir',xml,'--select-class',TESTTYPE])
        (store/'terminal.json').write_text(json.dumps(stages['junit'],indent=2)+'\n')
        assert junit.returncode==0,(junit.stdout,junit.stderr)
        report = xml/'TEST-junit-jupiter.xml'
        suite = ET.parse(report).getroot()
        [node] = suite.findall('testcase')
        assert successful_case(node)
        assert node.get('classname')==TESTTYPE and node.get('name')=='rejectsDeclaredOneWhenTheAnimationRecordsAreEmpty()'
        assert [suite.get(k) for k in ('tests','failures','errors','skipped')]==['1','0','0','0']
        measured = runpy.run_path('tools/quality/jacoco_readonly_exec_subset.py')['decode'](
            original_exec.read_bytes(),{PROJECTION})
        hits = measured['classes'][PROJECTION]
        assert hits['hitProbeIds'] and int(hits['crc64'],16)==int(class_crcs[PROJECTION],16)
        physical = {str(p.relative_to(classes)):pin(p)['sha256'] for p in locations}
    out = OPS/RUN
    out.mkdir()
    result = dict(actualExit=0,productionCore=plan['productionCoreMain'],testId='PT-WEB-SCR009-COUNT-001',
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(),os=platform.platform(),run=RUN,
                  newTests=1,failures=0,errors=0,skipped=0,notRun=0,stages=stages,testSource=pin(TEST),
                  existingTestReceipt=pin(old),retainedOldCases=16,replayedOldTests=0,sourceInputs=list(map(pin,sources)),
                  admittedDeps=pin(deps_source),currentPhysicalSha256=physical,currentClassCrc=class_crcs,
                  matchesOldCrc=same_earlier_crc,currentExecClass=hits,oldAndNewExecCombined=False,
                  localOriginals=list(map(pin,[store/'terminal.json',original_exec,report])),
                  observedCase=dict(classname=node.get('classname'),name=node.get('name')),
                  input=dict(declaredCount=1,actualRows=0),expected='IllegalArgumentException',
                  actual='IllegalArgumentException',wholeScopeCoverage=False,whole451=False,formalDelta=0)
    target=out/'manifest.json'
    with target.open('x') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(pin(target),same_earlier_crc)


if __name__=='__main__':
    main()
