"""Run the new memory port case and retain exact CRC, XML and terminal evidence."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


H = runpy.run_path(str(Path(__file__).with_name('5609_scr012_count_underclaim.py')))
BIN, OPS, WEB = (H[n] for n in ('BIN','OPS','WEB'))
pin, read, sha, check, successful_case = (H[k] for k in ('pin','read','sha','check','successful_case'))
PKG = 'dev/codex/schubert/nk/web/media'
CASE_OWNER = PKG.replace('/','.')+'.MediaRangePortTest'
CASE = 'directErrorBeforeResponseEscapesUnchangedAndReleasesThePermit'
TEST = WEB/'test/java'/PKG/'MediaRangePortTest.java'
FILES = ('MediaRangeService','HttpByteRangeParser','MediaBodyStreamer','MediaDeliveryException',
         'ContentDispositionFactory')
RUN = 'PG41194-media-range-error-releases-permit-v1'


def main():
    start, = Path('documents/400_PGPT/470_PMO').glob('601_*/1622_*.json')
    context = read(start)['values']
    assert all(pin(Path(ref['path']))==ref for ref in context['oracleReferences'])
    assert shutil.disk_usage('/dev/shm').free>=32*1024**2 and shutil.disk_usage('.').free>=64*1024**2
    current_sources = [WEB/'main/java'/PKG/(name+'.java') for name in FILES]
    for path in current_sources:
        source = subprocess.check_output(['git','show',f'{context["productionCoreMain"]}:{path}'],timeout=15)
        assert source==path.read_bytes()
    old_test = subprocess.check_output(['git','show',f'{context["source"]}:{TEST}'],timeout=15).decode()
    now = TEST.read_text()
    insert = re.search(r'\n  @Test\n  void '+CASE+r'\(\) throws Exception \{.*?\n  }\n',now,re.S)
    assert insert and now[:insert.start()]+now[insert.end():] != now
    inverted = (now[:insert.start()]+now[insert.end():]).replace('PT-MED-PORT001..009','PT-MED-PORT001..008')
    assert inverted==old_test
    prior, = OPS.glob('PG27000-*/manifest.json')
    original = read(prior)
    previous_cases = [x for x in original['cases'] if x['classname']==CASE_OWNER]
    assert len(previous_cases)==8
    assert all(not any(x[k] for k in ('failure','error','skipped')) for x in previous_cases)
    known_deps, = OPS.glob('PG37996-*/manifest.json')
    cached = read(known_deps)['dependencies']
    included = ['current-protocol176.jar','jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar']
    dependency_files = [Path(path) for path in cached if Path(path).name in included]
    assert {p.name for p in dependency_files}==set(included)
    assert all(pin(p)['sha256']==cached[str(p)] for p in dependency_files)
    measurement, = OPS.glob('PG38002-*/manifest.json')
    known_measure = read(measurement)
    agent_arg, = [arg for arg in known_measure['command'] if arg.startswith('-javaagent:')]
    agent = Path(agent_arg.split('=',1)[0].removeprefix('-javaagent:'))
    assert pin(agent)['sha256']==known_measure['measurementAgentSha256']
    format_tool = Path('../toolchain/google-java-format-1.36.1-all-deps.jar').resolve()
    style_tool = Path('../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar').resolve()
    cli = Path('../toolchain/org.jacoco.cli-0.8.15-nodeps.jar').resolve()
    stages = {}
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-media-error-') as scratch:
        classes = Path(scratch)/'classes'
        classes.mkdir()
        cp = os.pathsep.join(map(str,[classes,*dependency_files]))
        stages['format'], fmt = check([BIN/'java','-jar',format_tool,'--dry-run','--set-exit-if-changed',TEST])
        stages['checkstyle'], style = check([BIN/'java','-jar',style_tool,'-c','tools/quality/static/checkstyle.xml','-f','xml',TEST])
        assert fmt.returncode==style.returncode==0 and not ET.fromstring(style.stdout).findall('.//error')
        stages['compile'], compiled = check([BIN/'javac','--release','25','-Xlint:all','-Werror','-proc:none',
                                              '-cp',cp,'-d',classes,*current_sources,TEST])
        assert compiled.returncode==0,compiled.stderr
        product = [p for p in (classes/PKG).glob('*.class') if not p.name.startswith('MediaRangePortTest')]
        physical = {p.name:pin(p)['sha256'] for p in product}
        main = classes/PKG/'MediaRangeService.class'
        stages['crc'], classinfo = check([BIN/'java','-jar',cli,'classinfo',main])
        assert classinfo.returncode==0
        compiled_crc, = re.findall(rb'class 0x([0-9a-f]+) ',classinfo.stdout)
        durable = (Path('../pgpt-runs/PG379')/RUN).resolve()
        durable.mkdir()
        exec_path, xml_dir = durable/'unit.exec',durable/'xml'
        stages['junit'], executed = check([BIN/'java','-Dfile.encoding=UTF-8',
            f'-javaagent:{agent}=destfile={exec_path},append=false,sessionid={RUN}','-cp',cp,
            'org.junit.platform.console.ConsoleLauncher','execute','--disable-banner','--details=summary',
            '--fail-if-no-tests','--reports-dir',xml_dir,'--select-method',CASE_OWNER+'#'+CASE])
        terminal = durable/'terminal.json'
        terminal.write_text(json.dumps(stages['junit'],indent=2)+'\n')
        assert executed.returncode==0,(executed.stdout,executed.stderr)
        report = xml_dir/'TEST-junit-jupiter.xml'
        suite = ET.parse(report).getroot()
        [testcase] = suite.findall('testcase')
        assert testcase.get('classname')==CASE_OWNER and testcase.get('name')==CASE+'()'
        assert successful_case(testcase)
        assert [suite.get(k) for k in ('tests','failures','errors','skipped')]==['1','0','0','0']
        class_name = PKG+'/MediaRangeService'
        covered = runpy.run_path('tools/quality/jacoco_readonly_exec_subset.py')['decode'](
            exec_path.read_bytes(),{class_name})['classes'][class_name]
        assert int(covered['crc64'],16)==int(compiled_crc,16) and covered['hitProbeIds']
    out = OPS/RUN
    out.mkdir()
    content = dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),run=RUN,
                   productionCore=context['productionCoreMain'],testId='PT-MED-PORT009',testSource=pin(TEST),
                   previousEightByteExactApartFromNewCase=True,originalCaseReceipt=pin(prior),newTests=1,
                   failures=0,errors=0,skipped=0,notRun=0,oldTestsExecutedHere=0,
                   sourceInputs=list(map(pin,current_sources)),physical=physical,currentProbe=covered,
                   stages=stages,localOriginals=list(map(pin,[terminal,exec_path,report])),
                   verifiedEffects={'initialSameError':True,'initialBegins':0,'initialOpens':0,
                     'initialCloses':0,'nextStatus':206,'nextByteCount':3,'nextCloses':1},
                   realFileAuthHttpOrDbActions=0,whole451=False,formalDelta=0)
    manifest = out/'manifest.json'
    with manifest.open('x') as stream:
        json.dump(content,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(pin(manifest),len(physical))


if __name__=='__main__':
    main()
