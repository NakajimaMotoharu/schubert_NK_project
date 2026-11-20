"""Verify one new mismatch against the sealed track projection bytecode."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


H = runpy.run_path(str(Path(__file__).with_name('5609_scr012_count_underclaim.py')))
BIN, OPS, WEB = (H[k] for k in ('BIN','OPS','WEB'))
read, pin, sha, check, successful_case = (
    H[k] for k in ('read','pin','sha','check','successful_case'))
PROJECTION = 'dev/codex/schubert/nk/web/view/MusicTrackViewModel'
TESTTYPE = 'dev.codex.schubert.nk.web.view.MusicTrackCountBoundaryTest'
TEST = WEB/'test/java'/Path(TESTTYPE.replace('.', '/')+'.java')
RUN = 'PG41188-scr013-music-track-overclaimed-count-v1'


def main():
    start, = Path('documents/400_PGPT/470_PMO').glob('601_*/1616_*.json')
    context = read(start)['values']
    assert all(pin(Path(row['path']))==row for row in context['oracleReferences'])
    assert shutil.disk_usage('/dev/shm').free > 32*1024**2 and shutil.disk_usage('.').free > 64*1024**2
    prep, unit, post = [Path(row['path']) for row in context['oracleReferences'][1:]]
    prior = read(unit)
    proof = read(post)
    assert prior['actualExit']==prior['failures']==prior['errors']==prior['skipped']==proof['actualExit']==0
    [case] = [row for row in prior['cases'] if row['name']=='public003CountAffinityIdentityLengthAndOrderBounds()']
    assert not any(case[k] for k in ('failure','error','skipped'))
    selected_names = {'MusicTrackViewModel.java','TopBarViewModel.java','SessionPrincipal.java',
                      'MusicTrackPublicContractTest.java','AuthenticationContext.java','MusicTrackRecord.java',
                      'MusicTrackResponseData.java','DisplayPath.java','PairRole.java','UserRole.java'}
    source_inputs = {n:d for n,d in proof['inputHashes'].items() if Path(n).name in selected_names}
    assert {Path(p).name for p in source_inputs}==selected_names and len(source_inputs)==10
    for name, digest in source_inputs.items():
        current = subprocess.check_output(['git','show',f'{context["productionCoreMain"]}:{name}'],timeout=15)
        assert sha(current)==digest==pin(Path(name))['sha256']
    physical_name = PROJECTION+'.class'
    component = Path('../pgpt-runs/PG379/pg27774-music-track-public6-normal-v1/component')
    compiled = (component/physical_name).read_bytes()
    assert sha(compiled)==read(prep)['mainClassHashes'][physical_name]==proof['physicalClassHashes'][physical_name]
    dependencies_receipt, = OPS.glob('PG37996-*/manifest.json')
    wanted = {'current-protocol176.jar','jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar',
              'qualified-web-safe18.jar','spring-core-7.0.9.jar','spring-web-7.0.9.jar'}
    dependency_hashes = read(dependencies_receipt)['dependencies']
    dependencies = [Path(name) for name in dependency_hashes if Path(name).name in wanted]
    assert {p.name for p in dependencies}==wanted
    assert all(pin(p)['sha256']==dependency_hashes[str(p)] for p in dependencies)
    baseline, = OPS.glob('PG38002-*/manifest.json')
    agent_flag, = [entry for entry in read(baseline)['command'] if entry.startswith('-javaagent:')]
    agent = Path(agent_flag.split('=',1)[0].removeprefix('-javaagent:'))
    assert pin(agent)['sha256']==read(baseline)['measurementAgentSha256']
    style = Path('../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar').resolve()
    formatter = Path('../toolchain/google-java-format-1.36.1-all-deps.jar').resolve()
    stages = {}
    stages['format'], shaped = check([BIN/'java','-jar',formatter,'--dry-run','--set-exit-if-changed',TEST])
    stages['checkstyle'], checked = check([BIN/'java','-jar',style,'-c','tools/quality/static/checkstyle.xml','-f','xml',TEST])
    assert shaped.returncode==checked.returncode==0 and not ET.fromstring(checked.stdout).findall('.//error')
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-scr013-count-') as scratch:
        root = Path(scratch)
        class_file = root/physical_name
        class_file.parent.mkdir(parents=True)
        class_file.write_bytes(compiled)
        classpath = os.pathsep.join(map(str,[root,*dependencies]))
        stages['compile'], made = check([BIN/'javac','--release','25','-Xlint:all','-Werror','-proc:none',
                                        '-cp',classpath,'-d',root,TEST])
        assert made.returncode==0,made.stderr
        local = (Path('../pgpt-runs/PG379')/RUN).resolve()
        local.mkdir()
        exec_file, xml_dir = local/'unit.exec', local/'xml'
        stages['junit'], result = check([BIN/'java','-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
            f'-javaagent:{agent}=destfile={exec_file},append=false,sessionid={RUN}',
            '-cp',classpath,'org.junit.platform.console.ConsoleLauncher','execute','--disable-banner',
            '--details=summary','--fail-if-no-tests','--reports-dir',xml_dir,'--select-class',TESTTYPE])
        terminal = local/'terminal.json'
        terminal.write_text(json.dumps(stages['junit'],indent=2)+'\n')
        assert result.returncode==0,(result.stdout,result.stderr)
        xml_file = xml_dir/'TEST-junit-jupiter.xml'
        suite = ET.parse(xml_file).getroot()
        [node] = suite.findall('testcase')
        assert [suite.get(key) for key in ('tests','failures','errors','skipped')]==['1','0','0','0']
        assert node.get('classname')==TESTTYPE and node.get('name')=='rejectsDeclaredOneWhenTheTrackRecordsAreEmpty()'
        assert successful_case(node)
        raw = runpy.run_path('tools/quality/jacoco_readonly_exec_subset.py')['decode'](
            exec_file.read_bytes(),{PROJECTION})['classes'][PROJECTION]
        assert raw['hitProbeIds'] and int(raw['crc64'],16)==int(proof['classIds'][PROJECTION],16)
    out = OPS/RUN
    out.mkdir()
    value = dict(actualExit=0,productionCore=context['productionCoreMain'],
                 terminalAtUTC=datetime.now(timezone.utc).isoformat(),os=platform.platform(),run=RUN,
                 testId='PT-WEB-SCR013-COUNT-001',testSource=pin(TEST),qualifiedTrackPhysical={physical_name:sha(compiled)},
                 originalEvidence=[pin(prep),pin(unit),pin(post)],sourceInputs=source_inputs,
                 exactProjectionBinaryMatches=True,stages=stages,tests=1,failures=0,errors=0,skipped=0,notRun=0,
                 localOriginals=list(map(pin,[terminal,exec_file,xml_file])),projectionExec=raw,
                 input=dict(declaredCount=1,actualRows=0),expected='IllegalArgumentException',actual='IllegalArgumentException',
                 oldProductReplayed=0,oldAndNewExecCombined=False,actualBackendOperations=0,formalDelta=0,whole451=False)
    receipt = out/'manifest.json'
    with receipt.open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(pin(receipt))


if __name__=='__main__':
    main()
