"""Check SS333 range arithmetic one byte on either side of signed long overflow."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


H = runpy.run_path(str(Path(__file__).with_name('5609_scr012_count_underclaim.py')))
BIN, OPS, WEB = (H[k] for k in ('BIN','OPS','WEB'))
read, pin, sha, check, successful_case = (H[k] for k in ('read','pin','sha','check','successful_case'))
P = 'dev/codex/schubert/nk/web/media/HttpByteRangeParser'
TESTTYPE = 'dev.codex.schubert.nk.web.media.HttpByteRangeLongBoundaryTest'
TEST = WEB/'test/java'/Path(TESTTYPE.replace('.','/')+'.java')
MAIN = WEB/'main/java'/Path(P+'.java')
RUN = 'PG41190-range-long-cap-neighbors-v1'


def main():
    start, = Path('documents/400_PGPT/470_PMO').glob('601_*/1619_*.json')
    scope = read(start)['values']
    assert all(pin(Path(row['path'])) == row for row in scope['oracleReferences'])
    assert shutil.disk_usage('/dev/shm').free >= 32*1024**2 and shutil.disk_usage('.').free >= 64*1024**2
    proof_path, design = [Path(row['path']) for row in scope['oracleReferences'][1:]]
    proof = read(proof_path)
    assert proof['actualExit']==0 and proof['tests']==5 and proof['targetRawAll100']
    canon = subprocess.check_output(['git','show',f'{scope["canonicalDesignSource"]}:{design}'],timeout=15)
    assert b'Math.addExact/subtractExact' in canon and b'MAX_BODY = 1,048,576' in canon
    source = subprocess.check_output(['git','show',f'{scope["productionCoreMain"]}:{MAIN}'],timeout=15)
    assert source == MAIN.read_bytes()
    old_source = subprocess.check_output(['git','show',f'{proof["sourceCore"]}:{MAIN}'],timeout=15)
    assert source == old_source
    attempted_absent = subprocess.run(['git','cat-file','-e',f'{scope["source"]}:{TEST}'],
                                      capture_output=True,timeout=10,check=False)
    assert attempted_absent.returncode!=0
    engine, = OPS.glob('PG38002-*/manifest.json')
    used = read(engine)
    agent_option, = [p for p in used['command'] if p.startswith('-javaagent:')]
    agent = Path(agent_option.split('=',1)[0].removeprefix('-javaagent:'))
    assert pin(agent)['sha256']==used['measurementAgentSha256']
    console = Path('../toolchain/junit-platform-console-standalone-1.13.4.jar').resolve()
    sdk, = OPS.glob('PG37996-*/manifest.json')
    assert pin(console)['sha256']==read(sdk)['dependencies'][str(console)]
    style = Path('../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar').resolve()
    formatter = Path('../toolchain/google-java-format-1.36.1-all-deps.jar').resolve()
    tools = {}
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-range-long-') as scratch:
        classes = Path(scratch)/'classes'
        classes.mkdir()
        tools['format'], fmt = check([BIN/'java','-jar',formatter,'--dry-run','--set-exit-if-changed',TEST])
        tools['checkstyle'], cs = check([BIN/'java','-jar',style,'-c','tools/quality/static/checkstyle.xml','-f','xml',TEST])
        assert fmt.returncode==cs.returncode==0 and not ET.fromstring(cs.stdout).findall('.//error')
        tools['compile'], compile_stage = check([BIN/'javac','--release','25','-Xlint:all','-Werror',
            '-proc:none','-cp',console,'-d',classes,MAIN,TEST])
        assert compile_stage.returncode==0,compile_stage.stderr
        actual_files = sorted((classes/Path(P).parent).glob(Path(P).name+'*.class'))
        physical = {str(path.relative_to(classes)):sha(path.read_bytes()) for path in actual_files}
        assert len(physical)==5
        local = (Path('../pgpt-runs/PG379')/RUN).resolve()
        local.mkdir()
        original_exec, reports = local/'unit.exec',local/'xml'
        cp = os.pathsep.join(map(str,(classes,console)))
        tools['junit'], executed = check([BIN/'java','-Dfile.encoding=UTF-8',
            f'-javaagent:{agent}=destfile={original_exec},append=false,sessionid={RUN}','-cp',cp,
            'org.junit.platform.console.ConsoleLauncher','execute','--disable-banner','--details=summary',
            '--fail-if-no-tests','--reports-dir',reports,'--select-class',TESTTYPE])
        terminal = local/'terminal.json'
        terminal.write_text(json.dumps(tools['junit'],indent=2)+'\n')
        assert executed.returncode==0,(executed.stdout,executed.stderr)
        raw_report = reports/'TEST-junit-jupiter.xml'
        suite = ET.parse(raw_report).getroot()
        [case] = suite.findall('testcase')
        assert [suite.get(k) for k in ('tests','failures','errors','skipped')]==['1','0','0','0']
        assert case.get('classname')==TESTTYPE
        assert case.get('name')=='distinguishesTheLastRepresentableCapFromTheFirstOverflow()'
        assert successful_case(case)
        decoded = runpy.run_path('tools/quality/jacoco_readonly_exec_subset.py')['decode'](
            original_exec.read_bytes(),{P})['classes'][P]
        assert decoded['hitProbeIds']
        matches = {name:digest==proof['allPhysicalHashes'][name] for name,digest in physical.items()}
    limit = 2**63-1
    cap = 2**20
    start = limit-(cap-1)
    end = limit-1
    assert start+cap-1==limit and start+1+cap-1==limit+1 and end-start+1==1_048_575
    result = dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  testId='PT-MED-RANGE-LONG-001',productionCore=scope['productionCoreMain'],run=RUN,
                  canonicalSS333Sha256=sha(canon),sharedEarlierInputs=pin(proof_path),testSource=pin(TEST),
                  cases=1,vectors=2,failures=0,errors=0,skipped=0,notRun=0,stages=tools,
                  independentArithmetic=dict(total=limit,cap=cap,firstStart=start,end=end,length=end-start+1,
                    nextStart=start+1,expectedOverflowAfterMaximum=limit+1),
                  physical=physical,sameOldPhysical=matches,actualProbeRecords=decoded,
                  locallyPreserved=list(map(pin,[terminal,original_exec,raw_report])),
                  oldSuccessReplayed=0,actualHttpFsOrMediaActions=0,whole451=False,formalDelta=0)
    p = OPS/RUN/'manifest.json'
    p.parent.mkdir()
    with p.open('x') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(pin(p),matches)


if __name__=='__main__':
    main()
