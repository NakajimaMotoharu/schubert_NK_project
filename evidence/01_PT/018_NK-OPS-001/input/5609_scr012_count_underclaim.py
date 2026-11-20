"""Run the one new SCR012 test against admitted byte-identical projection classes."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile


ROOT = Path.cwd()
WEB = Path('src/schubert-nk-web/src')
PROTO = Path('src/schubert-nk-protocol/src/main/java')
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
OWNER = 'dev.codex.schubert.nk.web.view.MusicSectionCountBoundaryTest'
TEST = WEB/'test/java'/Path(OWNER.replace('.', '/')+'.java')
BIN = Path('../toolchain/jdk-25.0.4/bin').resolve()
TARGET = 'dev/codex/schubert/nk/web/view/MusicSectionViewModel'
RUN = 'PG41176-scr012-section-count-underclaim-fresh-proof-v1'


def sha(data):
    return sha256(data).hexdigest()


def pin(file):
    return dict(path=str(file),sha256=sha(file.read_bytes()))


def read(file):
    return json.loads(file.read_bytes())


def find(number):
    path, = OPS.glob(number+'-*/manifest.json')
    return path


def check(cmd):
    argv = list(map(str, cmd))
    result = subprocess.run(argv, capture_output=True, timeout=45)
    stage = dict(command=argv,exit=result.returncode,stdoutSha256=sha(result.stdout),
                 stderrSha256=sha(result.stderr))
    return stage, result


def main():
    group, = Path('documents/400_PGPT/470_PMO').glob('601_*/1598_*.json')
    context = read(group)['values']
    assert all(pin(Path(ref['path'])) == ref for ref in context['oracleReferences'])
    assert shutil.disk_usage('/dev/shm').free >= 32 * 1024**2
    assert shutil.disk_usage(ROOT).free >= 64 * 1024**2
    prepared_path, old_path, proof_path = map(find, ('PG37996','PG38002','PG38004'))
    prepared, old, proof = list(map(read, (prepared_path, old_path, proof_path)))
    assert pin(old_path) == proof['originalUnit'] and old['actualExit'] == proof['actualExit'] == 0
    assert all(old[key] == 0 for key in ('failures','errors','skipped','notRun'))
    assert len({c['name'] for c in old['cases'] if c['name'].startswith(('web247','web248')) and
                c['result']=='PASS'}) == 2
    model_main = WEB/'main/java'
    source_inputs = [model_main/Path(name+'.java') for name in (
        TARGET, 'dev/codex/schubert/nk/web/view/TopBarViewModel',
        'dev/codex/schubert/nk/web/session/SessionPrincipal')]
    source_inputs += [PROTO/Path('dev/codex/schubert/nk/protocol')/(name+'.java') for name in (
        'header/AuthenticationContext','layout/media/MusicSectionRecord',
        'layout/media/MusicSectionResponseData','layout/semantic/UserRole')]
    orig_test, = [Path(name) for name in old['inputHashes'] if name.endswith('MusicHierarchyViewModelTest.java')]
    source_inputs.append(orig_test)
    for target in source_inputs:
        actual = subprocess.check_output(['git','show',f'{context["productionCoreMain"]}:{target}'],timeout=15)
        assert sha(actual) == old['inputHashes'][str(target)] == pin(target)['sha256'], target
    included = ('current-protocol176.jar','jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar',
                'qualified-web-safe18.jar','spring-core-7.0.9.jar','spring-web-7.0.9.jar')
    dependencies = [Path(p) for p in prepared['dependencies'] if Path(p).name in included]
    assert {p.name for p in dependencies} == set(included)
    assert all(pin(p)['sha256'] == prepared['dependencies'][str(p)] for p in dependencies)
    shipped = {'current-protocol176.jar': ('dev/codex/schubert/nk/protocol/header/AuthenticationContext.class',
               'dev/codex/schubert/nk/protocol/layout/media/MusicSectionRecord.class',
               'dev/codex/schubert/nk/protocol/layout/media/MusicSectionResponseData.class'),
               'qualified-web-safe18.jar': ('dev/codex/schubert/nk/web/session/SessionPrincipal.class',
               'dev/codex/schubert/nk/web/view/TopBarViewModel.class')}
    for dependency in dependencies:
        if dependency.name in shipped:
            with ZipFile(dependency) as archive:
                for member in shipped[dependency.name]:
                    assert sha(archive.read(member)) == proof['allPhysicalHashes'][member]
    agent, = [arg.split('=',1)[0].removeprefix('-javaagent:') for arg in old['command'] if arg.startswith('-javaagent:')]
    assert pin(Path(agent))['sha256'] == old['measurementAgentSha256']
    component = Path(old['command'][7].split(os.pathsep)[1])
    owner_physical = {name:prepared['mainClassHashes'][name] for name in (TARGET+'.class',TARGET+'$Card.class')}
    config = ROOT/'tools/quality/static/checkstyle.xml'
    style_tool = Path('../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar').resolve()
    formatter = Path('../toolchain/google-java-format-1.36.1-all-deps.jar').resolve()
    stages = {}
    stages['format'], fmt = check([BIN/'java','-jar',formatter,'--dry-run','--set-exit-if-changed',TEST])
    stages['checkstyle'], cs = check([BIN/'java','-jar',style_tool,'-c',config,'-f','xml',TEST])
    assert fmt.returncode == cs.returncode == 0 and not ElementTree.fromstring(cs.stdout).findall('.//error')
    with TemporaryDirectory(dir='/dev/shm',prefix='pgpt-scr012-count-') as scratch:
        private = Path(scratch)
        active = private/'classes'
        for name, want in owner_physical.items():
            bytecode = (component/name).read_bytes()
            assert sha(bytecode) == want == proof['allPhysicalHashes'][name]
            target = active/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(bytecode)
        cp = os.pathsep.join(map(str,(active,*dependencies)))
        stages['compile-test'], compiled = check([BIN/'javac','--release','25','-Xlint:all','-Werror','-proc:none',
                                                  '-cp',cp,'-d',active,TEST])
        if compiled.returncode:
            raise RuntimeError(compiled.stderr.decode())
        preserved = Path('../pgpt-runs/PG379')/RUN
        preserved.mkdir()
        exec_file = preserved.resolve()/'unit.exec'
        xml = preserved.resolve()/'xml'
        stages['test'], junit = check([BIN/'java','-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
            f'-javaagent:{agent}=destfile={exec_file},append=false,sessionid={RUN}',
            '-cp',cp,'org.junit.platform.console.ConsoleLauncher','execute','--disable-banner',
            '--details=summary','--fail-if-no-tests','--reports-dir',xml,'--select-class',OWNER])
        (preserved/'terminal.json').write_text(json.dumps(stages['test'],indent=2)+'\n')
        if junit.returncode:
            raise RuntimeError(junit.stdout.decode()+junit.stderr.decode())
        xml_data = (xml/'TEST-junit-jupiter.xml').read_bytes()
        suite = ElementTree.fromstring(xml_data)
        tests = suite.findall('testcase')
        assert len(tests)==1 and tests[0].attrib['classname']==OWNER
        assert tests[0].attrib['name']=='rejectsDeclaredZeroWhenOneSectionRecordIsPresent()'
        nonpass = {'failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'}
        assert not any(child.tag in nonpass for child in tests[0])
        assert [suite.get(k) for k in ('tests','failures','errors','skipped')]==['1','0','0','0']
        new_exec = exec_file.read_bytes()
        measurement = runpy.run_path('tools/quality/jacoco_readonly_exec_subset.py')['decode'](new_exec,{TARGET})
        assert measurement['classes'][TARGET]['hitProbeIds']
        sections = {name:proof['classIds'][name] for name in proof['classIds'] if name == TARGET}
        assert int(measurement['classes'][TARGET]['crc64'],16)==int(sections[TARGET],16)
    output = OPS/RUN
    output.mkdir()
    path = output/'manifest.json'
    record = dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),run=RUN,
                  originalGroup=context['contextGroupId'],productionCore=context['productionCoreMain'],
                  testId='PT-WEB-SCR012-COUNT-001',testSource=pin(TEST),os=platform.platform(),
                  tests=1,failures=0,errors=0,skipped=0,notRun=0,stages=stages,
                  previousActualRun=pin(old_path),previousCoverage=pin(proof_path),oldTestsReplayed=0,
                  sourceInputs=list(map(pin,source_inputs)),pinnedCurrentPhysical=owner_physical,
                  selectedProbeRecord=measurement['classes'][TARGET],execSha256=sha(new_exec),xmlSha256=sha(xml_data),
                  sameCandidateOldFixtureSourceHashes=True,wholeCodeCoverageNewRun=False,execUnion=False,
                  input=dict(declaredSectionCount=0,actualSectionRows=1,singleRowTrackCount=9),
                  expected='IllegalArgumentException',actual='IllegalArgumentException',
                  datasourceActions=0,webServiceActions=0,sourceFixturesChanged=0,formalDelta=0)
    normalized = dict(suite={k:suite.get(k) for k in ('tests','failures','errors','skipped')},
                      testcase={k:tests[0].get(k) for k in ('classname','name')}, rawSha256=sha(xml_data))
    (output/'case.json').write_text(json.dumps(normalized,indent=2)+'\n')
    record['case']=pin(output/'case.json')
    record['localOriginals']=list(map(pin,(preserved/'terminal.json',exec_file,xml/'TEST-junit-jupiter.xml')))
    with path.open('x') as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(pin(path))


if __name__=='__main__':
    main()
