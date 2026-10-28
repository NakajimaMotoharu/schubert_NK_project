"""New-only JDK/JUnit reporter tool checks; no Product classpath, tests or coverage credit."""
import json
import os
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13726-shared-reporter-selftest-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13726-shared-reporter-selftest-v1'
FILES = ['SharedSelectedJunitReporterV1.java','ReporterToolFixturesV1.java','ReporterToolDriverV1.java']
PREFIX = 'dev.codex.schubert.nk.tooling.ReporterToolFixturesV1$'
LIBRARIES = {'junit-platform-launcher-1.13.4.jar','junit-platform-engine-1.13.4.jar','junit-platform-commons-1.13.4.jar','junit-jupiter-api-5.13.4.jar','junit-jupiter-engine-5.13.4.jar','opentest4j-1.3.0.jar','apiguardian-api-1.1.2.jar'}
KEYS = {'found','started','succeeded','failed','skipped','aborted','containerFailed','containerAborted','passed'}
CASES = [
 ('passing',0,dict(found=2,started=2,succeeded=2),{'Passing':['first','second']},0,0),
 ('two-passing',0,dict(found=3,started=3,succeeded=3),{'Passing':['first','second'],'OtherPassing':['other']},0,0),
 ('wrong-total',1,dict(found=2,started=2,succeeded=2),{'Passing':['first','second']},0,0),
 ('wrong-distribution',1,dict(found=3,started=3,succeeded=3),{'Passing':['first','second'],'OtherPassing':['other']},0,0),
 ('failing',1,dict(found=1,started=1,failed=1),{'Failing':['fails']},1,0),
 ('skipped',1,dict(found=1,skipped=1),{'Skipped':['skipped']},0,1),
 ('aborted',1,dict(found=1,started=1,aborted=1),{'Aborted':['aborted']},0,1),
 ('failed-container',1,dict(found=1,containerFailed=1),{'FailedContainer':[]},0,0),
 ('empty-tests',1,dict(),{'Empty':[]},0,0),
 ('empty-map',1,None,{},0,0),('zero-count',1,None,{},0,0),('invalid-name',1,None,{},0,0)]

def parse_summary(text):
    parts = [v.split('=',1) for v in text.split(';')];assert len(parts) == len(KEYS)
    value = dict(parts);assert set(value) == KEYS and value['passed'] in ['true','false']
    return {k:(v == 'true' if k == 'passed' else int(v)) for k,v in value.items()}

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    original = data.read_checked(data.BASE/'PG13692-broker-journal-whole-twelve-pt-v1/manifest.json','7477079a2578c48a56746a0511b2576b9ffced366d362c0739d1ff1ed58627b1')
    assert original['source'] == SOURCE and original['actualExit'] == 0
    sources = [data.ROOT/'tools/quality/architecture'/name for name in FILES]
    source_hashes = {str(p):data.sha(p.read_bytes()) for p in sources}
    dependencies = {p:h for p,h in original['begin']['dependencyHashes'].items() if Path(p).name in LIBRARIES}
    assert len(dependencies) == 7 and {Path(p).name for p in dependencies} == LIBRARIES
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    assert not any('/schubert-nk-' in p for p in dependencies)
    os.umask(0o077);SLOT.mkdir();classes = SLOT/'classes';classes.mkdir();runner.SLOT = SLOT
    classpath = os.pathsep.join(sorted(dependencies));jdk = runner.TC/'jdk-25.0.4/bin'
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,invocation=invocation,toolSourceHashes=source_hashes,dependencyHashes=dependencies,productTestsPlanned=0,productClassesOnClasspath=False,profiles=[r[0] for r in CASES]))
    compile_stage = runner.step('compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(classes),*[str(p) for p in sources]],SLOT,timeout=120)
    assert compile_stage['actualExit'] == 0 and not compile_stage['timedOut']
    results = [];public = {}
    for profile,expected_exit,counts,suites,expected_failures,expected_skipped in CASES:
        work = SLOT/profile;work.mkdir();xml = work/'xml'
        command = [str(jdk/'java'),'-cp',str(classes)+os.pathsep+classpath,'ReporterToolDriverV1',profile,str(xml)]
        stage = runner.step(profile,command,SLOT,timeout=30)
        data.write(work/'exit.safe.json',stage)
        assert stage['actualExit'] == expected_exit and not stage['timedOut']
        summary = None;xml_hashes = {};actual_suites = {};failures = skipped = 0
        if counts is None:
            assert not xml.exists()
        else:
            summary_path = xml/'summary.safe.txt';summary = parse_summary(summary_path.read_text())
            expected = {k:False if k == 'passed' else 0 for k in KEYS};expected.update(counts,passed=expected_exit == 0)
            assert json.dumps(summary,sort_keys=True) == json.dumps(expected,sort_keys=True)
            public[profile+'/summary.safe.txt'] = summary_path
            for path in sorted(xml.glob('TEST-*.xml')):
                raw = path.read_bytes();assert b'reporter-tool-only-failure' not in raw and b'reporter-tool-only-container-failure' not in raw
                root = ET.fromstring(raw);name = root.get('name');assert name.startswith(PREFIX)
                short = name.removeprefix(PREFIX);cases = root.findall('testcase')
                assert int(root.get('tests')) == len(cases) and root.get('errors') == '0'
                assert all(case.get('classname') == name for case in cases)
                actual_suites[short] = sorted(case.get('name') for case in cases)
                failures += int(root.get('failures'));skipped += int(root.get('skipped'))
                xml_hashes[path.name] = data.sha(raw);public[profile+'/'+path.name] = path
            assert actual_suites == {k:sorted(v) for k,v in suites.items()}
            assert failures == expected_failures and skipped == expected_skipped
        results.append(dict(profile=profile,expectedExit=expected_exit,actualExit=stage['actualExit'],timedOut=False,expectedOutcomeObserved=True,summary=summary,actualSuites=actual_suites,xmlHashes=xml_hashes,stage=stage,productTestsExecuted=0))
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in source_hashes.items()) and all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    verify(invocation);OUT.mkdir()
    for relative,path in public.items():
        target = OUT/relative;target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target);assert data.sha(target.read_bytes()) == data.sha(path.read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,toolSourceHashes=source_hashes,dependencyHashes=dependencies,compileStage=compile_stage,cases=results,toolChecks=12,positiveToolRuns=2,intendedNegativeToolRuns=10,productTestsExecuted=0,productClasspathsUsed=False,oldProductResultsTransferred=False,coverage=None,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()));print('tool-only expected outcomes12; Product PT0; intended nonzero child exits10 retained')

if __name__ == '__main__':main()
